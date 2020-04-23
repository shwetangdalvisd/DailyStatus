from flask import Flask
from flask_mongoalchemy import MongoAlchemy

app = Flask(__name__)
app.config['MONGOALCHEMY_DATABASE'] = 'blogapp'
app.config['MONGOALCHEMY_CONNECTION_STRING'] = 'mongodb+srv://shwetangdalvi:shwetsan1997@cluster0-3u1t0.mongodb.net/blogapp?retryWrites=true&w=majority'

db = MongoAlchemy(app)

class blogapp_record(db.Document):
	name = db.StringField()
	password = db.StringField()