from neomodel import config
from sanic import Sanic
from os import getenv
from dotenv import load_dotenv
import orjson
from services.posts_service import posts_service
from services.users_service import users_service
from services.customers_service import customers_service
from services.stores_service import stores_service
from services.comments_service import comments_service

load_dotenv()

config.DATABASE_URL = getenv("DATABASE_URL")

app = Sanic("App", dumps=orjson.dumps)
app.blueprint(posts_service)
app.blueprint(users_service)
app.blueprint(customers_service)
app.blueprint(stores_service)
app.blueprint(comments_service)
