from flask import render_template, flash, current_app
from flask_login import current_user, login_user, login_required, logout_user, fresh_login_required
from .. import login_manager
from flask import redirect, url_for, request
from .. import database
from . import users
import core.authentication.objects
from objects import RegisterForm, RegisterFormGroup, Group, GroupUserCollection, VideoConference, VideoConferenceForm


@users.route('/user_management', endpoint='user_management')
@fresh_login_required
def user_management():
    users = core.authentication.objects.User.get_all_users()
    return render_template("user_management.html", users=users)


@users.route('/show_user/<id>', endpoint='show_user')
@fresh_login_required
def show_user(id):
    user = core.authentication.objects.User.load_user_from_id(id=id)
    user_groups = GroupUserCollection.get_groups_of_user(id)
    return render_template("show_user.html", user=user, user_groups=user_groups)


# Activate or Deactivate User
@users.route('/toggle_activation/<id>', endpoint='toggle_activation')
@fresh_login_required
def toggle_activation(id):
    user = core.authentication.objects.User.load_user_from_id(id=id)
    if user.toogle_activation():
        flash('Successfully changed Activation')
    return render_template("show_user.html", user=user)


@users.route('/group_management', endpoint='group_management')
@fresh_login_required
def group_management():
    groups = Group.load_current_groups()
    return render_template("group_management.html", groups=groups)


@users.route('/register', endpoint='register', methods=['GET', 'POST'])
@fresh_login_required
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if not core.authentication.objects.User.load_user_from_username(username=form.username.data):
            user = core.authentication.objects.User(username=form.username.data, name=form.name.data,
                                                    email=form.email.data, ip_address=form.ip_address.data,
                                                    phone=form.phone.data, city=form.city.data, active=True)
            if user.save():
                return render_template("user_created.html", user=user)
        else:
            flash('A user with these information exists')
    return render_template("register_user.html", form=form)


@users.route('/deleteUser<id>', endpoint='deleteUser', methods=['GET', 'POST'])
@fresh_login_required
def deleteUser(id):
    core.authentication.objects.User.load_user_from_id(id=id).deleteUser()
    return redirect(url_for("users.group_management"))


@users.route('/deleteGroup<id>', endpoint='deleteGroup', methods=['GET', 'POST'])
@fresh_login_required
def deleteGroup(id):
    Group.load_group_from_id(id=id).deleteGroup()
    return redirect(url_for("users.group_management"))


@users.route('/registerGroup', endpoint='registerGroup', methods=['GET', 'POST'])
@fresh_login_required
def registerGroup():
    form = RegisterFormGroup()
    if form.validate_on_submit():
        group = Group(name=form.name.data)
        if group.save():
            return redirect(url_for("users.group_management"))
    return render_template("register_group.html", form=form)


@users.route('/register_first_user', endpoint='register_first_user')
def register_first_user():
    if not database.db.Users.find_one({'username': 'admin'}):
        core.authentication.objects.User(username='admin', password='admin', administrator=True, active=True).save()
        current_app.logger.info('User Created : username : admin / password : admin')
        flash('User Created')
    else:
        current_app.logger.info('User Exists : username : admin / password : admin')
        flash('User Exists')
    return render_template("flash_messages.html")


# Video Conference MANAGEMENT
@users.route('/videoConferences', endpoint='videoConferences', methods=['GET', 'POST'])
@fresh_login_required
def videoConferences(id):
    return render_template("members_management.html", group_id=id, members=members, not_members=not_members)


# MEMBER MANAGEMENT
@users.route('/memberManagement/<id>', endpoint='memberManagement', methods=['GET', 'POST'])
@fresh_login_required
def memberManagement(id):
    members = GroupUserCollection.get_all_users_of_group(id_group=id)
    not_members = GroupUserCollection.get_not_members(id_group=id)
    return render_template("members_management.html", group_id=id, members=members, not_members=not_members)


@users.route('/groupChanges', endpoint='groupChanges', methods=['GET', 'POST'])
@fresh_login_required
def groupChanges():
    group_id = request.form.get('group_id')
    remove_members = request.form.getlist('remove_members')
    add_members = request.form.getlist('add_members')
    GroupUserCollection.remove_users_from_group(remove_members, group_id)
    GroupUserCollection.add_users_to_group(add_members, group_id)
    flash("Changes were applied Successfully!")
    return redirect(url_for("users.memberManagement", id=group_id))


@users.route('/videoConferenceChanges', endpoint='videoConferenceChanges', methods=['GET', 'POST'])
@fresh_login_required
def videoConferenceChanges():
    group_id = request.form.get('group_id')
    remove_members = request.form.getlist('remove_members')
    add_members = request.form.getlist('add_members')
    GroupUserCollection.remove_users_from_group(remove_members, group_id)
    GroupUserCollection.add_users_to_group(add_members, group_id)
    flash("Changes were applied Successfully!")
    return redirect(url_for("users.memberManagement", id=group_id))


@users.route('/displayConference/<conference>', endpoint='displayConference', methods=['GET', 'POST'])
@fresh_login_required
def displayConference(conference):
    conference = VideoConference.get_video_conference(conference)
    return render_template('displayConference.html', conference=conference)


@users.route('/manageConferences', endpoint='manageConferences', methods=['GET', 'POST'])
@fresh_login_required
def manageConferences():
    return render_template('videoConferenceManagement.html', conferences=VideoConference.get_video_conferences())


@users.route('/register_conference', endpoint='register_conference', methods=['GET', 'POST'])
@fresh_login_required
def register_conference():
    form = VideoConferenceForm()
    if form.submit.data and form.validate_on_submit():
        groups = request.form.getlist('add_groups')
        VideoConference(groups=groups, users=[], name=form.name.data).save()
        return redirect(url_for('users.manageConferences'))
    return render_template("register_conference.html", form=form, groups=Group.load_current_groups())


@users.route('/unregister_user_from_group', endpoint='unregister_user_from_group', methods=['GET', 'POST'])
@fresh_login_required
def unregister_user_from_group():
    user_id = request.form.get('user_id')
    group_id = request.form.get('group_id')
    VideoConference.add_user_to_excluded_list(group_id, user_id)
    return ''
