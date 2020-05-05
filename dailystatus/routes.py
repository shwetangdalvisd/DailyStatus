from flask import render_template, url_for, flash, redirect, request,session,jsonify
from dailystatus import app, mongo, bcrypt,login_manager,mail,cache
from bson.json_util import dumps
from dailystatus.forms import LoginForm,RegisterForm,ProjectForm,AssignForms,StatusForm,DeleteForms,View_statusForm
from flask_login import login_user, current_user, logout_user, login_required,UserMixin
from bson.objectid import ObjectId
import json
from flask_mail import Message
import datetime


class JSONEncoder(json.JSONEncoder):
	def default(self, o):
		if isinstance(o, ObjectId):
			return str(o)
		return json.JSONEncoder.default(self, o)

class User(UserMixin):
	def __init__(self, email):
		self.email = email
	def get_id(self):
		return self.email

@login_manager.user_loader
def load_user(email):
	u = mongo.db.user.find_one({"mail_id" : email })
	if not u:
		return None
	return User(email=u['mail_id'])

@app.route("/")
@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('logout'))
	form = LoginForm()
	Uer = mongo.db.user
	if form.validate_on_submit():
		user = Uer.find_one({"mail_id": form.email.data})
		if user is not None and bcrypt.check_password_hash(user['password'], form.password.data):
			user_obj = User(email=user['mail_id'])
			login_user(user_obj)
			next_page = request.args.get('next')
			if user['role'] == "admin":
				return (redirect(url_for('Register')) if next_page else redirect(url_for('Register')))
			else:
				return (redirect(url_for('StatusUpdate')) if next_page else redirect(url_for('StatusUpdate')))
		else:
			flash('Login Unsuccessful. Please check email and password', 'danger')
	return render_template('login.html', title='Login', form=form)


@app.route("/register", methods=['GET', 'POST'])
@login_required
@cache.memoize(50)
def Register():
	User = mongo.db.user
	if current_user.is_authenticated:
		pass
	form = RegisterForm()
	if form.username.data and form.email.data and form.password.data and form.role.data is not None:
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
@login_required
@cache.memoize(50)
def Assign():
	if current_user.is_authenticated:
		pass
	form = AssignForms()
	choices = list(mongo.db.user.find())
	choicesp = list(mongo.db.project_team.find())
	User = mongo.db.user
	Project = mongo.db.project_team
	if form.username.data and form.project.data and form.projectteam.data is not None:
		for us in form.username.data: 
			NAU = Project.find_one({"project_name":form.project.data,"team_member.username":us})
			if NAU is None:
				teammember = User.find_one({"username" : us}, {"_id":0, "projects":0})
				teammember['Project_Team'] = form.projectteam.data
				Project.update({"project_name":form.project.data},{"$push":{"team_member":teammember}})
				User.update({"username":us},{ "$push":{"projects":form.project.data}})
				flash('Team-member '+us+' has been added!','success')
			else:
				flash('Team-member '+us+' is already part of team!','danger')

		return redirect(url_for('Assign'))

	return render_template('Assign.html',title='assign',form=form,choices=choices,choicesp=choicesp)

@app.route("/registerproject", methods=['GET', 'POST'])
@login_required
def RegisterProject():
	form = ProjectForm()
	Project = mongo.db.project_team
	if form.validate_on_submit():

		pro = Project.find_one({"project_name": form.Project.data})
		if pro is None:
			Project.insert({"project_name" :form.Project.data,"doc":form.doc.data,"Cromail" :form.Cromail.data})
			flash('Your project has been created!', 'success')
			return redirect(url_for('RegisterProject'))
		else:
			flash('Projectname already exist! Enter new Projectname', 'danger')
	return render_template('registerproject.html', title='RegisterProject', form=form)

@app.route("/statusupdate", methods=['GET', 'POST'])
@login_required
def StatusUpdate():
	TaskS = mongo.db.task_status
	em = current_user.get_id()
	form = StatusForm()
	def usd():
		usr = []
		usf = list(mongo.db.user.find({'mail_id':em}))
		for i in usf:
			s = i['projects']
			for e in s:
				usr.append(e)
		return usr
	choices = usd()
	usr = mongo.db.user.find_one({"mail_id":em})
	if form.project.data and form.date.data and form.jirano.data and form.status.data and form.env.data is not None:
		TaskS.insert({"project":form.project.data , "username":usr['username'] , "date":form.date.data , "jira_no":form.jirano.data , "desc":form.desc.data , "status":form.status.data,"env": form.env.data , "Comment":form.comments.data})
		flash('Your status has been updated','success')
		return redirect(url_for('StatusUpdate'))

	return render_template('statusupdate.html', title='StatusUpdate', form=form,choices=choices)

@app.route("/delete", methods=['GET', 'POST'])
@login_required
def DeleteD():
	User = mongo.db.user
	project = mongo.db.project_team
	form = DeleteForms()
	choices = list(mongo.db.user.find())
	choicesp = list(mongo.db.project_team.find())
	if form.radio.data == "user":
		if form.username.data is not None:
			project.update({},{"$pull":{"team_member":{"username":form.username.data}}}, multi=True)
			User.remove({"username":form.username.data})
			#msg = mongo.db.runCommand({"getLastError": 1})
			flash('user removed successfully'+form.username.data)
			return redirect(url_for('DeleteD'))
	elif form.radio.data == "project":
		if form.project.data is not None:
			User.update({},{'$pull':{'projects':form.project.data}}, multi=True)
			project.remove({'project_name':form.project.data})
			return redirect(url_for('DeleteD'))
	elif form.radio.data == "userdel":
		if form.project.data and form.username.data is not None:
			project.update_one({'project_name':form.project.data},{'$pull':{'team_member':{'username':form.username.data}}})
			User.update_one({'username':form.username.data},{'$pull':{'projects':form.project.data}})
			flash('user removed successfully'+form.radio.data)
			return redirect(url_for('DeleteD'))
	return render_template('delete.html', title='Delete', form=form,choicesp=choicesp,choices=choices)


@app.route("/_background_proccess",methods=['GET','POST'])
def _background_proccess():
	project = request.args.get('project')
	user = list(mongo.db.user.find({'project_team':project},{'team_member':1}))
	sd = []
	for s in user['team_member']:
		sd.append(s['username'])
	return jsonify (result = sd)

@app.route("/viewstatus", methods=['GET', 'POST'])
@login_required
def View_status():
	form = View_statusForm()
	if current_user.is_authenticated:
		pass
	else:
		return redirect(url_for('login'))
	stat=[]
	Status = mongo.db.task_status
	if form.project.data or form.username.data or form.date.data is not None and form.SendMail.data is None:
		stat = list(Status.find({"project" : form.project.data, "date" : form.date.data, "username": form.username.data}))
		return render_template('view-status.html', form=form, stat=stat)
	if form.project.data and form.username.data and form.SendMail.data is not None:
		stat = list(Status.find({"project" : form.project.data, "date" : form.date.data, "username": form.username.data}))
		msg = Message(subject='test',sender='shwetangdemo@gmail.com',recipients=['shwetang.dalvi@sts.in'],body='This is Test Mail for App')
		msg.html=render_template('Email.html',stat=stat)
		mail.send(msg)
		flash("Your Mail has been Send to Chief Reporting officer!!",'success')
		return render_template('view-status.html', form=form, stat=stat)

	return render_template('view-status.html', form=form, stat=stat)

@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))



