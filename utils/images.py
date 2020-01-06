import io
import logging
import os
from urllib.parse import urlparse

import requests
from django.conf import settings

log = logging.getLogger(__name__)


def upload_image_from_url(url):
    if not url:
        return None

    image_name = os.path.basename(urlparse(url).path)
    if "." not in image_name:
        image_name += ".jpg"

    try:
        image_data = io.BytesIO(requests.get(url).content)
    except requests.exceptions.RequestException:
        return None

    try:
        uploaded = requests.post(
            url=settings.MEDIA_UPLOAD_URL,
            params={
                "code": settings.MEDIA_UPLOAD_CODE
            },
            files={
                "media": (image_name, image_data)
            }
        )
    except requests.exceptions.RequestException:
        return None
    finally:
        image_data.close()

    if 200 <= uploaded.status_code <= 299:
        try:
            response_data = uploaded.json()
        except Exception as ex:
            log.exception(f"Error uploading avatar: {ex}")
            return None

        return response_data["uploaded"][0]

    return None
