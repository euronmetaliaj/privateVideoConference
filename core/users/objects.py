from flask_wtf import Form
from wtforms.fields import StringField, PasswordField, BooleanField, SubmitField, FileField, SelectMultipleField
from wtforms.validators import (DataRequired, Length, Regexp, EqualTo, Email, ValidationError, URL, Email, IPAddress)
from flask_login import UserMixin
from flask import current_app
from core import database
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
import core.authentication.objects


class RegisterForm(Form):
    name = StringField("Full Name:", validators=[DataRequired()])
    email = StringField("Email", [DataRequired("Please enter your email address."),
                                  Email("Please enter your email address.")])
    username = StringField("Username", validators=[DataRequired()])
    phone = StringField("Phone Number", validators=[DataRequired()])
    ip_address = StringField("IP Address", validators=[IPAddress()])
    city = StringField("City")

    submit = SubmitField("Register")


class RegisterFormGroup(Form):
    name = StringField("Full Name:", validators=[DataRequired()])

    submit = SubmitField("Register")


class VideoConferenceForm(Form):
    name = StringField("Full Name:", validators=[DataRequired()])
    submit = SubmitField("Register")


# USER CLASS
class Group():
    """
    Security Group
    Members are part of this group
    """

    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

    @classmethod
    def load_group_from_id(cls, id):
        group = database.db.Groups.find_one({'_id': ObjectId(id)})
        if group:
            return cls(name=group['name'], id=group['_id'])

    def deleteGroup(self):
        return database.db.Groups.delete_one({'_id': self.id})

    @staticmethod
    def load_current_groups():
        res = []
        groups = database.db.Groups.find({})
        print groups
        for group in groups:
            res.append(Group.load_group_from_id(group['_id']))

        return res

    def save(self):
        if not self.id:
            # Check if Group exists in database
            if not database.db.Groups.find_one({
                'name': self.name
            }):
                # Add Group to database
                database.db.Groups.insert({
                    'name': self.name
                })
                current_app.logger.info('A group with name ' + str(self.name) + ' has been created!')
                return True
            else:
                current_app.logger.info('A group with name ' + str(self.name) + ' exists!Cannot create new one!')
                return False


class GroupUserCollection():
    def __init__(self, id_group, id_user, id=None):
        self.id = id
        self.id_group = Group.load_group_from_id(id_group)
        self.id_user = core.authentication.objects.User.load_user_from_id(id_user)

    def save(self):
        rec = database.db.GroupUsers.find_one({'id_group': self.id_group.id, 'id_user': self.id_user.id})
        if not rec:
            rec = database.db.GroupUsers.insert({
                'id_group': ObjectId(self.id_group.id),
                'id_user': ObjectId(self.id_user.id)
            })
            if rec:
                return True
        else:
            return False

    @classmethod
    def load_group_user_from_id(cls, id):
        rec = database.db.GroupUsers.find_one({'_id': ObjectId(id)})
        if rec:
            return cls(id=rec['id'], id_group=rec['id_group'], id_user=rec['id_user'])

    @staticmethod
    def get_all_users_of_group(id_group):
        user_group_records = database.db.GroupUsers.find({'id_group': ObjectId(id_group)})
        rec = []
        for ugroup in user_group_records:
            print ugroup, 'UGROUP'
            rec.append(core.authentication.objects.User.load_user_from_id(id=str(ugroup['id_user'])))
        return rec

    @staticmethod
    def get_not_members(id_group):
        user_group_records = database.db.GroupUsers.find({'id_group': ObjectId(id_group)})
        user_ids = [x['id_user'] for x in user_group_records]
        not_members = database.db.Users.find({
            '_id': {"$nin": user_ids}
        })
        rec = []
        for user in not_members:
            if user['name']:
                rec.append(core.authentication.objects.User.load_user_from_id(id=user['_id']))
        return rec

    @staticmethod
    def delete_users_from_group(id_group):
        database.db.GroupUsers.remove({
            'id_group': ObjectId(id_group)
        })

    @staticmethod
    def delete_user_from_group(user_id, id_group):
        print "Deleteing user and group from database", user_id, id_group
        print database.db.GroupUsers.remove({
            'user_id': ObjectId(user_id),
            'id_group': ObjectId(id_group)
        })

    @staticmethod
    def get_groups_of_user(user_id):
        rec = database.db.GroupUsers.find({
            'id_user': ObjectId(user_id)
        })
        records = []
        for i in rec:
            records.append(Group.load_group_from_id(i['id_group']))
        return records

    @staticmethod
    def remove_users_from_group(users_id, id_group):
        for user_id in users_id:
            database.db.GroupUsers.remove({
                'id_group': ObjectId(id_group),
                'id_user': ObjectId(user_id)
            })

    @staticmethod
    def add_users_to_group(users_id, id_group):
        for user_id in users_id:
            database.db.GroupUsers.insert({
                'id_group': ObjectId(id_group),
                'id_user': ObjectId(user_id)
            })


class VideoConference():
    def __init__(self, id=None, groups=[], users=[], excluded_users=[], state=None, name=None):
        self.id = id
        self.groups = [ObjectId(group) for group in groups]
        self.users = [ObjectId(user) for user in users]
        self.state = state or 'new'
        self.name = name
        self.excluded_users = excluded_users

    def save(self):
        rec = database.db.VideoConference.insert({
            'groups': self.groups,
            'users': self.users,
            'state': 'created',
            'name': self.name,
            'excluded_users': self.excluded_users
        })
        if rec:
            return True
        else:
            return False

    @classmethod
    def get_video_conference(cls, id):
        conference = database.db.VideoConference.find_one({'_id': ObjectId(id)})
        if conference:
            print conference
            return cls(id=conference['_id'], name=conference['name'], groups=conference['groups'],
                       users=conference['users'], state=conference['state'],
                       excluded_users=conference['excluded_users'])
        else:
            return None

    @classmethod
    def get_video_conferences(cls):
        res = []
        conferences = database.db.VideoConference.find({})
        for conference in conferences:
            print conference
            res.append(VideoConference.get_video_conference(conference['_id']))
        return res

    def is_user_alloweded(self, user_id):
        if user_id in self.other_users:
            return True
        else:
            for group in self.groups:
                users = GroupUserCollection.get_all_users_of_group(group)
                for user in users:
                    if user.id == user_id:
                        return True
        return False

    def add_groups_to_conference(self, groups_id):
        # GET GROUPS FROM ID
        groups = [Group.load_group_from_id(x) for x in groups_id]
        database.db.GroupUsers.update({
            {'_id': self.id},
            {'$push': {
                'groups': groups
            }}
        })

    @staticmethod
    def add_user_to_excluded_list(conference_id, user_id):
        database.db.VideoConference.find_and_modify(
            {"_id": ObjectId(conference_id)},
            {"$push": {
                "excluded_users": str(user_id)
            }
            }
        )

    def get_all_users(self):
        res = []
        for i in self.groups:
            res.append(GroupUserCollection.get_all_users_of_group(str(i)))
        return res

    def get_all_users_json(self):
        res = []
        for i in self.groups:
            users = GroupUserCollection.get_all_users_of_group(str(i))
            for user in users:
                if str(user.id) not in self.excluded_users:
                    res.append({'id': user.id, 'name': user.name, 'state': 'Online'})
        return res
