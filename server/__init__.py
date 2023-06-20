# ENVIRONMENT VARIABLE
import os
from dotenv import load_dotenv
load_dotenv()
# TO USE FLASK
from flask import Flask

# TO USE SQL AS OUR DATABASE
from flask_sqlalchemy import SQLAlchemy

# IMPORT BCRYPT FOR PASSWORD
from flask_bcrypt import Bcrypt

# import the flask-login extension
from flask_login import LoginManager

# IMPORTING THE CORS APP
from flask_cors import CORS

# TO SEND MAILS
from flask_mail import Mail


# SETTING APP TO BE AN INSTANCE OF FLASK
app = Flask(__name__)

# CONFIG FOR OUR MAILS
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = 'True'
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv("EMAIL_PASS")
mail = Mail(app)

# CREATE SECRET TOKEN
app.config['SECRET_KEY'] = '4526aa8e4e008bb0ce8dfe40262b696f'
# CONFIGURING THE SQL LITE DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# CREATE AN SQL DATABASE INSTANCE
db = SQLAlchemy(app)

# CREATING AN INSTANCE OF THE BCRYPT 
bcrypt = Bcrypt(app)

# CREATING AN INSTANCE OF THE LOGIN MANAGER
login_manager = LoginManager(app)

# # CREATING AN INSTANCE OF THE CORS APP
# cors = CORS(app)

login_manager.login_view = 'login'

login_manager.login_message_category = 'info'

from server import routes