import requests
from base64 import b64encode
from os import getenv


def download_file_in_base64(url):
    response = requests.get(url)
    base64_bytes = b64encode(response.content)
    base64_string = base64_bytes.decode("utf-8")

    return base64_string
