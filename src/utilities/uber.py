import requests
import json
from os import getenv
from dotenv import load_dotenv


load_dotenv()


def _format_phone_number(raw_phone_number):
    formatted_phone_number = f"+506{raw_phone_number}"

    return formatted_phone_number


def _call_uber_api(payload):
    customer_id = getenv("UBER_CUSTOMER_ID")
    client_id = getenv("UBER_CLIENT_ID")
    client_secret = getenv("UBER_CLIENT_SECRET")

    access_token_response = requests.post(
        'https://login.uber.com/oauth/v2/token',
        data={
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials',
            'scope': 'eats.deliveries',
        }
    )
    access_token_response.raise_for_status()

    access_token = access_token_response.json()["access_token"]

    delivery_response = requests.post(
        f'https://api.uber.com/v1/customers/{customer_id}/deliveries',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
        },
        json=payload
    )

    print("UBER LOG", delivery_response.text)
    delivery_response.raise_for_status()

    delivery = delivery_response.json()

    return delivery


def start_uber_delivery(customer, customer_location, store, store_location, sale):
    payload = {
        "pickup_address": json.dumps({
            "street_address": [store_location.street_address],
            "city": store_location.city,
            "state": store_location.state,
            "zip_code": store_location.zip_code
        }),
        "pickup_name": store_location.place_name,
        "pickup_phone_number": _format_phone_number(store.phone_number),
        "pickup_latitude": store_location.latitude,
        "pickup_longitude": store_location.longitude,
        "dropoff_name": customer_location.place_name,
        "dropoff_phone_number": _format_phone_number(customer.phone_number),
        "dropoff_latitude": customer_location.latitude,
        "dropoff_longitude": customer_location.longitude,
        "dropoff_address": json.dumps({
            "street_address": [customer_location.street_address],
            "city": customer_location.city,
            "state": customer_location.state,
            "zip_code": customer_location.zip_code
        }),
        "manifest_items": [
            {
                "quantity": sale.amount
            }
        ],
        "test_specifications": {
            "robo_courier_specification": {
                "mode": "auto"
            }
        },
        "undeliverable_action": "leave_at_door"
    }

    delivery = _call_uber_api(payload)

    return delivery
