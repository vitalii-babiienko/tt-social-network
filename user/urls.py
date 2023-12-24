from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from user.views import (
    CreateUserView,
    ManageUserView,
    ShowUserActivityView,
)

urlpatterns = [
    path("signup/", CreateUserView.as_view(), name="create_user"),
    path("me/", ManageUserView.as_view(), name="manage_user"),
    path(
        "activity/",
        ShowUserActivityView.as_view(),
        name="show_user_activity",
    ),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]

app_name = "user"
