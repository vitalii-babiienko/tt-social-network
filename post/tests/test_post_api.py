from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from post.models import Post
from post.serializers import (
    PostListSerializer,
    PostDetailSerializer,
)

POST_LIST_URL = reverse("post:post-list")
NUMBER_OF_POSTS = 5
PAGINATION_COUNT = 5


def create_posts(author):
    return [
        Post.objects.create(
            author=author,
            title=f"Title {i}",
            content=f"Content {i}",
        )
        for i in range(NUMBER_OF_POSTS)
    ]


def detail_url(post_id):
    return reverse("post:post-detail", args=[post_id])


def like_unlike_url(post_id):
    return reverse("post:post-like-unlike-post", args=[post_id])


class UnauthenticatedPostApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(POST_LIST_URL)

        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPostApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test_user",
            email="test@test.com",
            first_name="test first",
            last_name="test last",
            password="test_pass",
        )
        self.client.force_authenticate(self.user)

    def test_list_posts(self):
        create_posts(self.user)

        res = self.client.get(POST_LIST_URL)

        posts = Post.objects.order_by("-created_at")
        serializer = PostListSerializer(posts, many=True)

        self.assertEquals(res.status_code, status.HTTP_200_OK)

        for i in range(PAGINATION_COUNT):
            for key in serializer.data[i]:
                self.assertEquals(
                    res.data["results"][i][key],
                    serializer.data[i][key],
                )

    def test_retrieve_post_detail(self):
        create_posts(self.user)

        post = Post.objects.all()[0]

        url = detail_url(post.id)
        res = self.client.get(url)

        serializer = PostDetailSerializer(post)

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(res.data, serializer.data)

    def test_like_unlike_post(self):
        create_posts(self.user)

        post = Post.objects.all()[0]

        url = like_unlike_url(post.id)
        res = self.client.post(url)

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertIn(self.user, post.likes.all())

        res = self.client.post(url)

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.user, post.likes.all())

    def test_add_comment(self):
        create_posts(self.user)

        post = Post.objects.all()[0]

        payload = {
            "author": self.user.id,
            "post": post.id,
            "content": "Test Content",
        }
        res = self.client.post(
            reverse("post:post-add-comment", args=[post.id]),
            payload,
        )

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(
            "{'detail': 'Your comment has been successfully added to the post.'}",
            str(res.data),
        )
