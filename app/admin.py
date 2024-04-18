import jwt

from sqladmin import ModelView, Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from datetime import datetime, timedelta

from app.models import (
    LaunchpadProject,
    ProxyLink,
    ProjectImage,
    OnRampOrder,
    TokenDetails,
    ProjectLink,
)

from app.env import ADMIN_PASSWORD, ADMIN_USERNAME, TOKEN_EXPIRATION, ALGORITHM, SECRET_KEY


class LaunchpadProjectAdmin(ModelView, model=LaunchpadProject):
    column_list = [LaunchpadProject.slug, LaunchpadProject.name, LaunchpadProject.created_at]


class ProxyLinkAdmin(ModelView, model=ProxyLink):
    column_list = [ProxyLink.base_url, ProxyLink.project_id]


class ProjectImageAdmin(ModelView, model=ProjectImage):
    pass


class OnrampOrderAdmin(ModelView, model=OnRampOrder):
    pass


class TokenDetailsAdmin(ModelView, model=TokenDetails):
    pass


class ProjectLinkAdmin(ModelView, model=ProjectLink):
    pass


admin_views = [
    LaunchpadProjectAdmin,
    ProjectLinkAdmin,
    ProjectImageAdmin,
    OnrampOrderAdmin,
    TokenDetailsAdmin,
    ProxyLinkAdmin,
]


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        if not username == ADMIN_USERNAME or not password == ADMIN_PASSWORD:
            return False

        token = self._generate_token(username)
        request.session.update({"token": token})

        return True

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

    @staticmethod
    def _generate_token(username: str) -> str:
        expiration_time = datetime.utcnow() + timedelta(minutes=int(TOKEN_EXPIRATION))
        payload = {"username": username, "exp": expiration_time}
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


authentication_backend = AdminAuth(secret_key=SECRET_KEY)


def add_views(admin: Admin):

    for view in admin_views:
        admin.add_view(view)
