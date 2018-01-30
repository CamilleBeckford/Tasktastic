from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin

app * Flask(_name_)
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://root:jamaicanoproblem@localhost/task manager'
app.config['SECRET_KEY']='shhh'

db = SQLAlchemy(app)
login_manager=LoginManager()
login_manager init_app(app)

class User(UserMixin, db.Model):
	id= db.Column(db.Integer, primary_key=True )
	username = db.Column(db.String(30),unique=True)

