import datetime
import requests


def fetch_access_token_response(client_id, client_secret):
    authentication_url = "https://login.uber.com/oauth/v2/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": "eats.deliveries"
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(authentication_url, headers=headers, data=payload)
    response.raise_for_status()

    json = response.json()

    return json


def parse_future_datetime_from_seconds(seconds):
    difference = datetime.timedelta(seconds)
    current_datetime = datetime.datetime.now()
    future_datetime = current_datetime + difference

    return future_datetime


class UberDirectClient:
    def __init__(self, customer_id, client_id, client_secret):
        response = fetch_access_token_response(client_id, client_secret)

        self.customer_id = customer_id
        self.access_token = response["access_token"]
        self.expiration_datetime = parse_future_datetime_from_seconds(
            response["expires_in"]
        )

    def _do_json_post_request(self, endpoint_name, payload):
        url = (
            f"https://api.uber.com/v1/customers/{self.customer_id}/{endpoint_name}"
        )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        json = response.json()

        return json

    def has_access_token_expired(self):
        current_datetime = datetime.datetime.now()

        return self.expiration_datetime < current_datetime

    def refresh_access_token(self):
        response = fetch_access_token_response(
            self.client_id,
            self.client_secret
        )

        self.access_token = response["access_token"]
        self.expiration_datetime = parse_future_datetime_from_seconds(
            response["expires_in"]
        )

    def get_quote(self, payload):
        if self.has_access_token_expired():
            self.refresh_access_token()

        json = self._do_json_post_request("delivery_quotes", payload)

        return json

    def create_delivery(self, payload):
        if self.has_access_token_expired():
            self.refresh_access_token()

        json = self._do_json_post_request("deliveries", payload)

        return json
