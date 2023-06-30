from neomodel import config
from sanic import Sanic
from os import getenv
from dotenv import load_dotenv
import orjson

load_dotenv()

config.DATABASE_URL = getenv("DATABASE_URL")

from services.posts_service import posts_service

app = Sanic("App", dumps=orjson.dumps)
app.blueprint(posts_service)
