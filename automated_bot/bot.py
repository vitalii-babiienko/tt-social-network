import random

import requests

from automated_bot.config import rules, api_base_url


class SocialNetworkBot:
    def __init__(self, rules, api_base_url) -> None:
        self.rules = rules
        self.api_base_url = api_base_url
        self.users = {}

    def signup_users(self) -> None:
        for user_id in range(self.rules.get("number_of_users")):
            user_data = {
                "username": f"user_{user_id}",
                "password": "password$$$",
            }
            self._make_request("POST", "user/signup/", data=user_data)
            user_data["posts"] = {}
            self.users[user_id] = user_data

    def login_users(self) -> None:
        for user_id, user_data in self.users.items():
            response = self._make_request(
                "POST",
                "user/token/",
                data=user_data,
            )
            self.users[user_id]["token"] = response.get("access")

    def create_posts(self) -> None:
        for user_id in self.users:
            token = self.users[user_id]["token"]
            max_posts_number = random.randint(
                1, self.rules.get("max_posts_per_user")
            )
            for post_id in range(max_posts_number):
                post_data = {
                    "title": f"Post by user #{user_id}",
                    "content": f"Some content in the post #{post_id}",
                }
                response = self._make_request(
                    "POST", "post/", data=post_data, token=token
                )
                self.users[user_id]["posts"][post_id] = {
                    "post_id": response.get("id"),
                    "likes": set(),
                }

    def like_posts(self) -> None:
        for user_id in self.users:
            token = self.users[user_id]["token"]
            max_likes_number = random.randint(
                1, self.rules.get("max_likes_per_user")
            )
            already_liked_posts = dict()
            for _ in range(max_likes_number):
                target_user_id = random.choice(list(self.users.keys()))
                target_post_id = random.choice(
                    list(self.users[target_user_id]["posts"].keys())
                )
                if already_liked_posts.get(target_user_id) is None:
                    already_liked_posts[target_user_id] = []
                if target_post_id in already_liked_posts[target_user_id]:
                    continue
                already_liked_posts[target_user_id].append(target_post_id)
                target_post_data = (
                    self.users[target_user_id]["posts"][target_post_id]
                )
                post_id = str(target_post_data["post_id"])
                self._make_request(
                    "POST",
                    f"post/{post_id}/like-unlike/",
                    token=token,
                )
                target_post_data["likes"].add(user_id)

    def _make_request(self, method, endpoint, data=None, token=None):
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        url = f"{self.api_base_url}{endpoint}"
        response = requests.request(
            method=method, url=url, json=data, headers=headers
        )
        return response.json() if response.ok else None

    def display_activity(self) -> None:
        for user_id, user_data in self.users.items():
            print(f"User {user_id}:")
            for post_id, post_data in user_data["posts"].items():
                likes = ", ".join(map(str, post_data["likes"]))
                print(
                    f"  Post {post_id} with id #{post_data['post_id']} "
                    f"was liked by users: [{likes}]"
                )


if __name__ == "__main__":
    bot = SocialNetworkBot(rules, api_base_url)
    bot.signup_users()
    bot.login_users()
    bot.create_posts()
    bot.like_posts()
    bot.display_activity()
