from neomodel import config
from sanic import Sanic
from os import getenv
from blueprints.posts_blueprint import posts_blueprint
from dotenv import load_dotenv

load_dotenv()

config.DATABASE_URL = getenv("DATABASE_URL")

app = Sanic("App")
app.blueprint(posts_blueprint)

