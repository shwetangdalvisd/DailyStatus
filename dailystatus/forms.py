from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectMultipleField, DateField,SelectField,TextField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,Optional
from dailystatus import app, mongo
from flask_login import login_user, current_user

class LoginForm(FlaskForm):
	email = StringField('Email',validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')


class RegisterForm(FlaskForm):
	username = StringField('Username',validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email',validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
	role = SelectField('Role',validators=[DataRequired()])
	submit = SubmitField('Sign Up')

class ProjectForm(FlaskForm):
	Project = StringField('Project Name',validators=[DataRequired()])
	doc = StringField('Date of Completion')
	Cromail = StringField('CRO Email',validators=[Optional(), Email()])
	submit = SubmitField('submit')

def usf():
	us = []
	usr = list(mongo.db.user.find())
	for s in usr:
		us.append(s['username'])
	return us
def pjf():
	pj = []
	pjt = list(mongo.db.project_team.find())
	for i in pjt:
		pj.append(i['project_name'])
	return pj

class AssignForms(FlaskForm):
	username = SelectMultipleField('username',choices=usf())
	project = SelectField('project',choices=pjf())
	projectteam = SelectField('projectteam')
	submit = SubmitField('submit')

class StatusForm(FlaskForm):
	project = SelectField('Project',validators=[DataRequired()])
	date = DateField('Date',format='%d/%m/%Y',validators=[DataRequired()])
	jirano = StringField('Jira NO.',validators=[DataRequired()])
	desc = TextField('Description',validators=[DataRequired()])
	status = SelectField('username',validators=[DataRequired()])
	env = SelectField('Env',validators=[DataRequired()])
	comments = TextField('Comment', validators=[DataRequired()])
	submit = SubmitField('submit')

class View_statusForm(FlaskForm):
	project = SelectField('Project', choices=pjf())
	username = SelectField('Username',choices=usf())
	date = StringField('Date')
	submit = SubmitField('submit')

class DeleteForms(FlaskForm):
	username = SelectMultipleField('username',choices=usf(),validators=[Optional()])
	project = SelectField('project',choices=pjf(),validators=[Optional()])
	submit = SubmitField('submit')




