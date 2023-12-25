from django.urls import path
from rest_framework import routers

from post.views import (
    HashtagViewSet,
    PostViewSet,
    LikesAnalyticsView,
)

router = routers.DefaultRouter()
router.register("hashtags", HashtagViewSet)
router.register("", PostViewSet)

urlpatterns = [
    path("analytics/", LikesAnalyticsView.as_view(), name="analytics"),
] + router.urls

app_name = "post"
