from flask import render_template, flash
from flask_login import current_user, login_user, login_required, logout_user, fresh_login_required
from . import authentication
from objects import LoginForm
from .objects import User
from .. import login_manager

from flask import redirect, url_for


@login_manager.user_loader
def load_user(id):
    user = User.load_user_from_id(id)
    return user


@authentication.route('/dashboard', endpoint='dashboard')
@fresh_login_required
def dashboard():
    return render_template('dashboard.html')


@authentication.route('/', methods=["GET", "POST"])
@authentication.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated():
        return redirect(url_for('authentication.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        # login and validate user
        user = User.load_user(form.username.data, form.password.data)
        if user:
            login_user(user)
            return redirect(url_for('authentication.dashboard'))
        flash("Incorrect username or password")
    return render_template("login.html", form=form)


@authentication.route('/logout')
@login_required
def logout():
    logout_user()
    flash('User has been logged out successfully')
    return redirect(url_for('authentication.login'))
