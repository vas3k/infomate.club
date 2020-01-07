import logging
from datetime import datetime

import jwt
from django.conf import settings
from django.shortcuts import redirect, render

from auth.models import Session

log = logging.getLogger()


def login(request):
    return redirect(f"{settings.AUTH_REDIRECT_URL}?redirect={settings.APP_HOST}/auth/club_callback/")


def club_callback(request):
    token = request.GET.get("jwt")
    if not token:
        return render(request, "message.html", {
            "title": "Что-то пошло не так",
            "message": "При авторизации потерялся токен. Попробуйте войти еще раз."
        })

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except (jwt.DecodeError, jwt.ExpiredSignatureError) as ex:
        log.error(f"JWT token error: {ex}")
        return render(request, "message.html", {
            "title": "Что-то сломалось",
            "message": "Неправильный ключ. Наверное, что-то сломалось. Либо ты ХАКИР!!11"
        })

    Session.objects.get_or_create(
        token=token[:1024],
        defaults=dict(
            user_id=payload["user_id"],
            user_name=str(payload.get("user_name") or "")[:32],
            expires_at=datetime.utcfromtimestamp(payload["exp"])
        )
    )

    response = redirect("index")
    response.set_cookie(settings.AUTH_COOKIE_NAME, token, max_age=settings.AUTH_COOKIE_MAX_AGE)
    return response


def logout(request):
    token = request.COOKIES.get(settings.AUTH_COOKIE_NAME)
    if token:
        Session.objects.filter(token=token).delete()

    response = redirect("index")
    response.delete_cookie(settings.AUTH_COOKIE_NAME)
    return response
