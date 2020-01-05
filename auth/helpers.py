from datetime import datetime

import jwt
from django.conf import settings
from django.shortcuts import render


def authorized_user(request):
    token = request.COOKIES.get(settings.AUTH_COOKIE_NAME)
    if not token:
        return None

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except (jwt.DecodeError, jwt.ExpiredSignatureError) as ex:
        response = render(request, "message.html", {
            "title": "Что-то сломалось",
            "message": "Неправильный токен авторизации. Наверное, что-то сломалось. "
                       "Либо вы ХАКИР!!11 (тогда идите в жопу)"
        })
        response.delete_cookie(settings.AUTH_COOKIE_NAME)
        return response

    if datetime.utcfromtimestamp(payload["exp"]) < datetime.utcnow():
        return None

    return payload
