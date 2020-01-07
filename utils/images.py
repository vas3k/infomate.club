import io
import logging
import os
from urllib.parse import urlparse

import requests
from PIL import Image
from django.conf import settings

log = logging.getLogger(__name__)


def upload_image_from_url(url, resize=(192, 192), convert_format="PNG"):
    if not url:
        return None

    image_name = os.path.basename(urlparse(url).path)
    if "." not in image_name:
        image_name += ".jpg"

    try:
        image_data = io.BytesIO(requests.get(url).content)
    except requests.exceptions.RequestException:
        return None

    if resize:
        try:
            image = Image.open(image_data)
        except OSError:
            log.warning(f"Broken image file: {url}")
            return None

        image.thumbnail(resize)
        saved_image = io.BytesIO()
        image.save(saved_image, format=convert_format, optimize=True)
        image_data = saved_image.getvalue()
        image_name = os.path.splitext(image_name)[0] + f".{convert_format.lower()}"

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
    except requests.exceptions.RequestException as ex:
        log.error(f"Image upload error: {ex}")
        return None

    if 200 <= uploaded.status_code <= 299:
        try:
            response_data = uploaded.json()
        except Exception as ex:
            log.exception(f"Image upload error: {ex} ({uploaded.content})")
            return None

        return response_data["uploaded"][0]

    return None
