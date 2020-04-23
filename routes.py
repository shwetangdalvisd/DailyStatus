from flask import render_template, url_for, flash, redirect, request,session
from daily import app, mongo, bcrypt
from dailystatus.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/login", methods=['GET', 'POST'])
def login():
    return render_template('login.html', title='Login', form=form)
