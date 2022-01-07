from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = '45af1ff116fa160b425e2d03204afef4' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.sqlite'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_message_category = "warning"
login_manager.login_view = 'login'

migrate = Migrate(app, db, compare_type=True)

from application import routes
