# -*- coding: utf-8 -*-
"""
    flaskbb.admin.forms
    ~~~~~~~~~~~~~~~~~~~~

    It provides the forms that are needed for the admin views.

    :copyright: (c) 2013 by the FlaskBB Team.
    :license: BSD, see LICENSE for more details.
"""
from datetime import datetime

from flask.ext.wtf import Form
from wtforms import (TextField, TextAreaField, PasswordField, IntegerField,
                     BooleanField, SelectField, DateField)
from wtforms.validators import (Required, Optional, Email, EqualTo, regexp,
                                ValidationError, URL, Length)

from wtforms.ext.sqlalchemy.fields import (QuerySelectField,
                                           QuerySelectMultipleField)

from flaskbb.helpers import SelectDateWidget
from flaskbb.forum.models import Category, Forum
from flaskbb.user.models import User, Group

USERNAME_RE = r'^[\w.+-]+$'
is_username = regexp(USERNAME_RE,
                     message=("You can only use letters, numbers or dashes"))


def selectable_categories():
    return Category.query.order_by(Category.id)


def select_primary_group():
    return Group.query.order_by(Group.id)


def select_secondary_groups():
    return Group.query.order_by(Group.id)


class UserForm(Form):
    username = TextField("Username", validators=[
        Required(message="Username required"),
        is_username])

    email = TextField("E-Mail", validators=[
        Required(message="Email adress required"),
        Email(message="This email is invalid")])

    password = PasswordField("Password", validators=[
        Required(message="Password required")])

    birthday = DateField("Birthday", format="%d %m %Y",
                         widget=SelectDateWidget(),
                         validators=[Optional()])

    gender = SelectField("Gender", default="None", choices=[
        ("None", ""),
        ("Male", "Male"),
        ("Female", "Female")])

    location = TextField("Location", validators=[
        Optional()])

    website = TextField("Website", validators=[
        Optional(), URL()])

    avatar = TextField("Avatar", validators=[
        Optional(), URL()])

    signature = TextAreaField("Forum Signature", validators=[
        Optional(), Length(min=0, max=250)])

    notes = TextAreaField("Notes", validators=[
        Optional(), Length(min=0, max=5000)])

    primary_group = QuerySelectField("Primary Group",
                                     query_factory=select_primary_group,
                                     get_label="name")

    #secondary_groups = QuerySelectMultipleField(
    #    "Secondary Groups", query_factory=select_secondary_groups,
    #    allow_blank=True, get_label="name")

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError("This username is taken")

    def validate_email(self, field):
        email = User.query.filter_by(email=field.data).first()
        if email:
            raise ValidationError("This email is taken")

    def save(self):
        user = User(date_joined=datetime.utcnow(),
                    **self.data)
        return user.save()


class GroupForm(Form):
    name = TextField("Group Name", validators=[
        Required(message="Group name required")])

    description = TextAreaField("Description", validators=[
        Optional()])

    admin = BooleanField("Is Admin Group?",
                         description="With this option the group has access \
                                     to the admin panel.")
    super_mod = BooleanField("Is Super Moderator Group?",
                             description="Check this if the users in this \
                                         group are allowed to moderate every \
                                         forum")
    mod = BooleanField("Is Moderator Group?",
                       description="Check this if the users in this group are \
                                   allowed to moderate specified forums")
    banned = BooleanField("Is Banned Group?",
                          description="Only one Banned group is allowed")
    guest = BooleanField("Is Guest Group?",
                         description="Only one Guest group is allowed")
    editpost = BooleanField("Can edit posts",
                            description="Check this if the users in this \
                                        group can edit posts")
    deletepost = BooleanField("Can delete posts",
                              description="Check this is the users in this \
                                          group can delete posts")
    deletetopic = BooleanField("Can delete topics",
                               description="Check this is the users in this \
                                           group can delete topics")
    posttopic = BooleanField("Can create topics",
                             description="Check this is the users in this \
                                         group can create topics")
    postreply = BooleanField("Can post replies",
                             description="Check this is the users in this \
                                         group can post replies")

    def save(self):
        group = Group(**self.data)
        return group.save()

    def validate_banned(self, field):
        if Group.query.filter_by(banned=True).count >= 1:
            raise ValidationError("There is already a Banned group")

    def validate_guest(self, field):
        if Group.query.filter_by(guest=True).count() >= 1:
            raise ValidationError("There is already a Guest group")


class ForumForm(Form):
    title = TextField("Forum Title", validators=[
        Required(message="Forum title required")])

    description = TextAreaField("Description", validators=[
        Optional()])

    position = IntegerField("Position", validators=[
        Required(message="Forum position required")])

    category = QuerySelectField("Category",
                                query_factory=selectable_categories,
                                get_label="title")

    def save(self, category):
        forum = Forum(**self.data)
        return forum.save(category=category)


class CategoryForm(Form):
    title = TextField("Category Title", validators=[
        Required(message="Category title required")])

    description = TextAreaField("Description", validators=[
        Optional()])

    position = IntegerField("Position", validators=[
        Required(message="Forum position required")])

    def save(self):
        category = Category(**self.data)
        return category.save()