from slowapi import Limiter

from app.env import settings
from app.utils import get_ip_from_request

limiter = Limiter(key_func=get_ip_from_request, storage_uri=str(settings.redis_url))
