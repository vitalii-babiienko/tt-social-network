from datetime import datetime, timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from post.models import (
    Hashtag,
    Post,
)
from post.paginations import (
    HashtagPagination,
    PostPagination,
)
from post.permissions import (
    IsPostOwnerOrReadOnly,
)
from post.serializers import (
    HashtagSerializer,
    PostSerializer,
    PostListSerializer,
    PostDetailSerializer,
    PostImageSerializer,
    CommentAddSerializer,
)


class UploadImageMixin:
    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading the image to the specific instance"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=["Hashtags"])
class HashtagViewSet(viewsets.ModelViewSet):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = HashtagPagination

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list":
            name = self.request.query_params.get("name")

            if name:
                queryset = queryset.filter(name__icontains=name)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="name",
                type=str,
                description="Filter by name (ex. ?name=FREEDOM)",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema(tags=["Posts"])
class PostViewSet(UploadImageMixin, viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, IsPostOwnerOrReadOnly)
    pagination_class = PostPagination

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list":
            title = self.request.query_params.get("title")
            author = self.request.query_params.get("author")

            if title:
                queryset = queryset.filter(title__icontains=title)

            if author:
                queryset = queryset.filter(author__username__icontains=author)

        queryset = (
            queryset
            .select_related("author")
            .prefetch_related(
                "hashtags",
                "comments__author",
            )
            .annotate(
                likes_count=Count("likes", distinct=True),
                comments_count=Count("comments", distinct=True),
            )
            .order_by("-created_at")
        )

        return queryset

    def get_serializer_class(self):
        if self.action in (
            "list",
            "show_favorite_posts",
        ):
            return PostListSerializer

        if self.action == "retrieve":
            return PostDetailSerializer

        if self.action == "upload_image":
            return PostImageSerializer

        if self.action == "add_comment":
            return CommentAddSerializer

        return PostSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="like-unlike",
        permission_classes=[IsAuthenticated],
    )
    def like_unlike_post(self, request, pk=None):
        """Endpoint for liking/unliking posts feature"""
        post = self.get_object()
        user = self.request.user

        if user not in post.likes.all():
            post.likes.add(user)
            return Response(
                {"detail": "You have successfully liked the post."},
                status=status.HTTP_200_OK,
            )

        post.likes.remove(user)
        return Response(
            {"detail": "Your like was successfully removed."},
            status=status.HTTP_200_OK,
        )

    @action(
        methods=["GET"],
        detail=False,
        url_path="favorite",
        permission_classes=[IsAuthenticated],
    )
    def show_favorite_posts(self, request):
        """Endpoint for showing a list of the favorite posts"""
        user = self.request.user
        posts = Post.objects.filter(likes=user)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        detail=True,
        url_path="add-comment",
        permission_classes=[IsAuthenticated],
    )
    def add_comment(self, request, pk=None):
        """Endpoint for adding a comment to the post"""
        user = self.request.user
        post = self.get_object()
        serializer = CommentAddSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save(
            author=user,
            post=post,
            content=serializer.validated_data["content"],
        )
        return Response(
            {
                "detail": "Your comment has been successfully "
                          "added to the post."
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="title",
                type=str,
                description="Filter by title (ex. ?title=Numpy)",
                required=False,
            ),
            OpenApiParameter(
                name="author",
                type=str,
                description="Filter by author (ex. ?author=Jack)",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class LikesAnalyticsView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["Likes Analytics"],
        parameters=[
            OpenApiParameter(
                name="date_from",
                type=str,
                description="Start date for analytics (YYYY-MM-DD)",
                required=True,
            ),
            OpenApiParameter(
                name="date_to",
                type=str,
                description="End date for analytics (YYYY-MM-DD)",
                required=True,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        date_from_param = request.GET.get("date_from", "")
        date_to_param = request.GET.get("date_to", "")

        if not date_from_param or not date_to_param:
            return Response(
                {"error": "Both date_from and date_to are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            date_from = datetime.strptime(date_from_param, "%Y-%m-%d")
            date_to = (datetime.strptime(date_to_param, "%Y-%m-%d")
                       + timedelta(days=1))
        except ValueError:
            return Response(
                {"error": "Invalid date format"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        analytics_data = Post.objects.filter(
            likes__isnull=False,
            created_at__range=(date_from, date_to)
        ).annotate(
            day=TruncDate("created_at")
        ).values(
            "day"
        ).annotate(
            likes_count=Count("likes")
        )

        response_data = [
            {
                "date": item["day"].strftime("%Y-%m-%d"),
                "likes_count": item["likes_count"],
            }
            for item in analytics_data
        ]

        return Response(response_data, status=status.HTTP_200_OK)
