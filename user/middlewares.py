from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken


class UserLastRequestTimeMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request) -> Response:
        authorization_header = request.headers.get("Authorization", "")

        if authorization_header:
            raw_token = authorization_header.split()[1]

            try:
                access_token = AccessToken(token=raw_token)
                user = get_user_model().objects.get(id=access_token["user_id"])
                user.last_request_time = timezone.now()
                user.save()
            except TokenError as e:
                print(e)

        response = self.get_response(request)
        return response
