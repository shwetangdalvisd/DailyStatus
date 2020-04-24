from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectMultipleField, DateField,SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,Optional
from dailystatus import app, mongo


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
	role = StringField('Role',validators=[DataRequired()])
	submit = SubmitField('Sign Up')

class ProjectForm(FlaskForm):
	Project = StringField('Project Name',validators=[DataRequired()])
	doc = StringField('Date of Completion')
	Cromail = StringField('Email',validators=[DataRequired(), Email()])
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
 




