from rest_framework import routers

from post.views import (
    HashtagViewSet,
    PostViewSet,
)

router = routers.DefaultRouter()
router.register("hashtags", HashtagViewSet)
router.register("", PostViewSet)

urlpatterns = router.urls

app_name = "post"
