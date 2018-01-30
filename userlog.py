from flask import Flask, request, render_template
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore,UserMixin, RoleMixin, login_required
from flask.ext.security.utils import encrypt_password
from flask.ext.security.registerable import register_user
from datetime import datetime
from flask_table import Table, Col

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://root:jamaicanoproblem@localhost/task manager'
app.config['SECRET_KEY'] = 'super-secret'
app.config['CSRF_ENABLED'] = True
app.config['USER_ENABLED_EMAIL'] = False
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = '0fd571c2653fbbf4126ffcc4fbbffa25'

db= SQLAlchemy(app)

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    tasks= db.relationship('Tasks',backref='user',lazy=True)

class Tasks (db.Model):
	__tablename__='tasks'
	id = db.Column(db.Integer, primary_key=True)
	description = db.Column(db.String(255))
	category =db.Column(db.String(255))
	due = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
	notes= db.Column(db.String(255))
	remind= db.Column(db.Boolean())
	priority= db.Column(db.Integer)
	user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
	subtask=db.relationship('SubTasks',backref='tasks',lazy=True)

# def __init__(self,description):
# 	self.description=description

class SubTasks(db.Model):
	
	id = db.Column(db.Integer, primary_key=True)
	description = db.Column(db.String(255))
	category =db.Column(db.String(255))
	due = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
	notes= db.Column(db.String(255))
	remind= db.Column(db.Boolean())
	priority= db.Column(db.Integer)
	tasks_id=db.Column(db.Integer,db.ForeignKey('tasks.id'),nullable=False)
	

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Create a user to test with
@app.before_first_request
def create_user():
    #user_datastore.create_user(email='can@test.fr', password=encrypt_password('testword'))
    #user_datastore.create_user(email='m@nobien.net', password='test')
    db.session.commit()

@app.route("/")
@login_required
def index():
   return render_template('index.html')

@app.route('/load', methods=["GET", "POST"])
def load():
	tasklist=Tasks.query.all()
	return render_template('index.html',tasklist=tasklist)


@app.route('/log/<uid>', methods=["GET", "POST"])
def log(uid):
	    
	tasks=Tasks(description=request.form['description'],user_id=uid)
	db.session.add(tasks)
	db.session.commit()
	load()

	return render_template('index.html')


@app.route('/api/delete/<keys>')
def delete(keys):
	task = Tasks.query.get(keys)
	db.session.delete(task)
	db.session.commit()
	tasklist=Tasks.query.all()
	return render_template('index.html',tasklist=tasklist)

if __name__ == '__main__':
   app.run(debug = True)

##localhost:9283/api/delete/hello