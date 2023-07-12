from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)
app.config['SECRET_KEY'] = '3c8e082904b2543fc543b3f86046d158'
""" Add secret key to protect against modifying cookies,CSRF
    Use:
        import secrets
        secrets.token_hex(#number_of_bytes)
"""
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
"""
Location of database, Relative Path.
"""
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.app_context().push()

db = SQLAlchemy(app)
"""
SQLAchemy instance of the database.
"""

bcrypt = Bcrypt(app)
"""
Creates and validates a registration management system.
bcrypt instance for hashing passwords for security purposes 
and then using it to very that the password is corect. 
Plain text passwords make a vulnerability.
"""

login_manager=LoginManager(app)
"""
Creates a login management system for login sessions for users
to login and logout.
Handles all the sessions in the background.
"""

login_manager.login_view = 'login'
login_manager.login_message = 'You need to login to access your account details'
login_manager.login_message_category = 'info'

from application import routes
