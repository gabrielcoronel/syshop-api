from sanic import Sanic
from sanic_cors import CORS
from neomodel import config
import orjson
from os import getenv
from dotenv import load_dotenv

from services.posts_service import posts_service
from services.users_service import users_service
from services.customers_service import customers_service
from services.stores_service import stores_service
from services.comments_service import comments_service
from services.chat_service import chat_service
from services.categories_service import categories_service
from services.locations_service import locations_service
from services.sales_service import sales_service
from services.deliveries_service import deliveries_service

load_dotenv()

config.DATABASE_URL = getenv("DATABASE_URL")

app = Sanic(__name__, dumps=orjson.dumps)
CORS(app)

app.blueprint(posts_service)
app.blueprint(users_service)
app.blueprint(customers_service)
app.blueprint(stores_service)
app.blueprint(comments_service)
app.blueprint(chat_service)
app.blueprint(categories_service)
app.blueprint(locations_service)
app.blueprint(sales_service)
app.blueprint(deliveries_service)
