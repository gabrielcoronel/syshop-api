import requests
import google
from base64 import b64encode
from os import getenv


def download_file_in_base64(url):
    response = requests.get(url)
    base64_bytes = b64encode(response.content)
    base64_string = base64_bytes.decode("utf-8")

    return base64_string


def validate_google_id_token(token):
    google_api_client_id = getenv("GOOGLE_API_CLIENT_ID")

    try:
        user_information = google.oauth2.id_token.verify_oauth2_token(
            token,
            google.auth.transport.requests.Request(),
            google_api_client_id
        )

        return (user_information, True)
    except ValueError:
        return (None, False)
