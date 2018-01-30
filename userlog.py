from flask import Flask, request, render_template
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore,UserMixin, RoleMixin, login_required
from flask.ext.security.utils import encrypt_password
from flask.ext.security.registerable import register_user
from datetime import datetime
from flask_table import Table, Col
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, BooleanField, PasswordField,SubmitField,SelectField
from flask_login import current_user

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

class EditForm(FlaskForm):
    description = StringField('Description')
    category = StringField('Category')
    notes = StringField('Notes')
    priority = StringField('Priority')
    subtask = StringField('Subtask')
    #subtask = BooleanField('Subtask')
    submit = SubmitField('Update')
	

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
	tasklist=Tasks.query.filter_by(user_id=current_user.id)
	return render_template('index.html',tasklist=tasklist)


@app.route('/log/<uid>', methods=["GET", "POST"])
def log(uid):
	    
	tasks=Tasks(description=request.form['description'],category=request.form['category'], due=request.form['due'], notes=request.form['notes'],
		priority=request.form['priority'],user_id=uid)
	db.session.add(tasks)
	db.session.commit()
	tasklist=Tasks.query.filter_by(user_id=current_user.id)
	return render_template('index.html',tasklist=tasklist)


@app.route('/api/delete/<keys>')
def delete(keys):
	task = Tasks.query.get(keys)
	db.session.delete(task)
	db.session.commit()
	tasklist=Tasks.query.all()
	return render_template('index.html',tasklist=tasklist)

@app.route('/api/edit/<keys>')
def edit(keys):
	form = EditForm()
	return render_template('editpage.html', form=form,taskid=keys)

@app.route('/api/update/edit/<keys>/update',methods=["GET", "POST"])
def Update(keys):
	if request.form['subtask']=='Subtask':
		subtask=SubTasks(description=request.form['description'],tasks_id=keys)
		db.session.add(subtask)
		db.session.commit()
		return render_template('index.html')

	else:
		if request.form['description']!='':
			task=Tasks.query.filter_by(id=keys).first()
			task.description=request.form['description']
			db.session.commit()
		if request.form['category']!='':
			task=Tasks.query.filter_by(id=keys).first()
			task.category=request.form['category']
			db.session.commit()
		if request.form['notes']!='':
			task=Tasks.query.filter_by(id=keys).first()
			task.notes=request.form['notes']
			db.session.commit()
		if request.form['priority']!='':
			task=Tasks.query.filter_by(id=keys).first()
			task.priority=request.form['priority']
			db.session.commit()

		return render_template('index.html')

@app.route('/api/subs/<keys>')
def subs(keys):
	subtask=SubTasks.query.filter_by(tasks_id=keys)
	return render_template('subtasksview.html', subtask=subtask)


	

if __name__ == '__main__':
   app.run(debug = True)

