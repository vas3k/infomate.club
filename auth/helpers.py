from datetime import datetime

import jwt
from django.conf import settings


def authorized_user(request):
    token = request.COOKIES.get(settings.AUTH_COOKIE_NAME)
    if not token:
        return None

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except (jwt.DecodeError, jwt.ExpiredSignatureError):
        return None

    if datetime.utcfromtimestamp(payload["exp"]) < datetime.utcnow():
        return None

    return payload
