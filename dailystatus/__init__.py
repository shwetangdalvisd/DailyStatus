from flask import Flask
from flask_pymongo import PyMongo
from bson.json_util import dumps
from flask import jsonify, request
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config["MONGO_URI"] = 'mongodb+srv://shwetangdalvi:shwetsan1997@cluster0-3u1t0.mongodb.net/blogapp?retryWrites=true&w=majority'
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'


mongo = PyMongo(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


from dailystatus import routes