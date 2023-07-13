import stripe
from os import getenv
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = getenv("STRIPE_SECRET_KEY")


def create_stripe_account():
    stripe_account = stripe.Account.create(
        business_type="individual",
        country="US",
        type="custom",
        capabilities={
            "card_payments": {
                "requested": True
            },
            "transfers": {
                "requested": True
            }
        },
    )

    return stripe_account
