from os import getcwd, path
import yaml
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from .lib.arguments import parse_args

args, _ = parse_args()

CONFIG_FILE_PATH = path.join(getcwd(), 'cfg', 'settings.yaml')
if path.isfile(CONFIG_FILE_PATH):
    with open(CONFIG_FILE_PATH, 'r') as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
else:
    cfg = {}

if args.config:
    with open(args.config, 'r') as f:
        cfg = {**cfg, **yaml.load(f, Loader=yaml.FullLoader)}


# TODO: 
# Refactor application initiantion to particular module
app = Flask(__name__)

if cfg["db"]["type"] == 'mysql':
    app.config['SQLALCHEMY_DATABASE_URI'] = cfg["db"]["url"]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JSON_AS_ASCII'] = False

db = SQLAlchemy(app, engine_options=cfg["db"]["engine"])
migrate = Migrate(app, db, directory='db/migrations')

app.config['SECRET_KEY'] = cfg["auth"]["secret-key"]
