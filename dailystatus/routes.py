from flask import render_template, url_for, flash, redirect, request,session,jsonify
from dailystatus import app, mongo, bcrypt,login_manager
from bson.json_util import dumps
from dailystatus.forms import LoginForm,RegisterForm,ProjectForm,AssignForms
from flask_login import login_user, current_user, logout_user, login_required,UserMixin
from bson.objectid import ObjectId
import json

class JSONEncoder(json.JSONEncoder):
	def default(self, o):
		if isinstance(o, ObjectId):
			return str(o)
		return json.JSONEncoder.default(self, o)

class User(UserMixin):
	def __init__(self, user_id):
		self.user_id = user_id
	def get_id(self):
		return (self.user_id)


@login_manager.user_loader
def load_user(user_id):
	u = mongo.db.Users.find_one({"user_id": user_id})
	if not u:
		return None
	return User(user_id=u['user_id'])

@app.route("/")
@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('Register'))
	form = LoginForm()
	Uer = mongo.db.user
	if form.validate_on_submit():
		user = Uer.find_one({"mail_id": form.email.data})
		if user is not None and bcrypt.check_password_hash(user['password'], form.password.data):
			sd = JSONEncoder().encode(user)
			user_obj = User(sd)
			login_user(user_obj)
			if user['role'] == "admin":
				return redirect(url_for('Register'))
			else:
				return redirect(url_for('StatusUpdate'))
		else:
			flash('Login Unsuccessful. Please check email and password', 'danger')
	return render_template('login.html', title='Login', form=form)


@app.route("/register", methods=['GET', 'POST'])
def Register():
	User = mongo.db.user
	if current_user.is_authenticated:
		return redirect(url_for('Register'))
	form = RegisterForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User.find_one({"mail_id": form.email.data})
		if user is None:
			User.insert({"username" : form.username.data, "mail_id" : form.email.data, "password" : hashed_password,"role" : form.role.data})
			flash('Your account has been created! You are now able to log in', 'success')
			return redirect(url_for('Register'))
		else:
			flash('Username already exist! Enter new Username', 'danger')


	return render_template('register.html', title='Register', form=form)



@app.route("/Assign",methods=['GET','POST'])
def Assign():
	if current_user.is_authenticated:
		return redirect(url_for('Assign'))
	form = AssignForms()
	User = mongo.db.user
	Project = mongo.db.project_team
	if form.username.data and form.project.data and form.projectteam.data is not None:
		for us in form.username.data:
			sd = us 
			teammember = User.find_one({"username" : us})
			projectn = Project.find_one({"project":form.project.data})
			Project.update({"project":form.project.data}, { "$set": { "teammember":teammember } }, multi=True)
			Project.find_and_modify(query = {"project": form.project.data, 'project.teammember' : us},update = { "$push": {"project_team":form.projectteam.data} })
			User.update({"username":form.username.data},{ "$push":{"projects":form.project.data}})
			flash('Team-member has been added!','success')
		return redirect(url_for('Assign'))

	return render_template('Assign.html',title='assign',form=form)

@app.route("/registerproject", methods=['GET', 'POST'])
def RegisterProject():
	form = ProjectForm()
	Project = mongo.db.project
	if form.validate_on_submit():

		pro = Project.find_one({"project_name": form.Project.data})
		if pro is None:
			Project.insert({"project_name" :form.Project.data,"doc":form.doc.data,"Cromail" :form.Cromail.data})
			flash('Your project has been created!', 'success')
			return redirect(url_for('RegisterProject'))
		else:
			flash('Projectname already exist! Enter new Projectname', 'danger')
	return render_template('registerproject.html', title='RegisterProject', form=form)

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('login'))

