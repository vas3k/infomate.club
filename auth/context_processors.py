from auth.helpers import authorized_user


def me(request):
    return {
        "me": authorized_user(request)
    }
