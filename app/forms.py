from wtforms import Form, BooleanField, StringField, PasswordField, validators, IntegerField, SelectField
from wtforms.widgets import TextArea, HiddenInput
from wtforms.fields.html5 import DecimalRangeField
from app import models, db
from flask.ext.login import current_user
from sqlalchemy import func
from reddit_api import praw_instance

class RegistrationForm(Form):
    username = StringField('Display Name', [validators.InputRequired(message="You need a username."), validators.Length(min=3, max=20, message ="Usernames can be between 3 and 20 characters."), validators.Regexp(r'^[\w_-]+$', message='Usernames can only contain letters, numbers, "-" and "_".')])
    email = StringField('Email', [validators.Optional(strip_whitespace=False), validators.Email()])
    bio = StringField('Bio', [validators.Length(max=140)], widget=TextArea())
    avatar = IntegerField('Avatar')
    favorite_sub_1 = StringField('Favorite Sub 1', [validators.InputRequired(message="We need at least on favorite sub to find matches.")])
    favorite_sub_2 = StringField('Favorite Sub 2', [validators.Optional()])
    favorite_sub_3 = StringField('Favorite Sub 3', [validators.Optional()])

    def validate(self):
        has_error = False

        rv = Form.validate(self)
        if not rv:
            return False

        user = models.User.query.filter(func.lower(models.User.username) == func.lower(self.username.data)).first()

        # if username is taken
        if user is not None:
            # if username isn't taken by current user
            print current_user.username.lower()
            print user.username.lower()

            if current_user.username is not user.username:
                self.username.errors.append('Username not available.')

                return False

        email_user = models.User.query.filter(func.lower(models.User.email) == func.lower(self.email.data)).first()

        # if email is taken by a user
        if email_user is not None:

            # if email isn't taken by current user
            if current_user.email is not email_user.email:
                self.email.errors.append('An account with that email already exists.')
                return False

        # check if subreddits exist
        favorite_subs = []
        favorite_subs.append(self.favorite_sub_1.data)

        if self.favorite_sub_2.data:
            favorite_subs.append(self.favorite_sub_2.data)

        if self.favorite_sub_3.data:
            favorite_subs.append(self.favorite_sub_3.data)

        for sub in favorite_subs:

            # strip /r/ from name
            if '/' in sub:
                sub = sub.split('/')[-1]


            # if subreddit isn't found in reddimatch db
            if models.Subreddit.query.filter_by(name = sub).first() is None:
                r = praw_instance()
                try:
                    r.get_subreddit(sub, fetch=True)
                except Exception as e:
                    index = favorite_subs.index(sub)

                    if index is 0:
                        favorite_sub = self.favorite_sub_1
                    if index is 1:
                        favorite_sub = self.favorite_sub_2
                    if index is 2:
                        favorite_sub = self.favorite_sub_3

                    favorite_sub.errors.append("We couldn't find that subreddit. Are you sure it's spelled correctly?")

                    return False

        self.user = user
        return True

    def update_user(self):
        pass

class DateRegistrationForm(Form):
    age = IntegerField('Age', [validators.InputRequired(message = "Age is required."), validators.NumberRange(min=18, max=130, message="You must be 18 years or older.")])
    gender =  SelectField('Gender', coerce=int, validators = [validators.InputRequired()], choices=[(1,'Man'), (2,'Woman'), (3,'Transgender')])
    desired_gender =  SelectField('Desired Gender', coerce=int, validators = [validators.InputRequired()], choices=[(1,'Man'), (2,'Woman'), (3,'Transgender')])
    radius = IntegerField('Radius', widget=HiddenInput(), validators = [validators.NumberRange(min=5, max=101)])
    min_age = IntegerField('Minimum Age', widget=HiddenInput(), validators = [validators.InputRequired(), validators.NumberRange(min=18, max=130)])
    max_age = IntegerField('Max Age', widget=HiddenInput(), validators = [validators.InputRequired(), validators.NumberRange(min=18, max=130)])
    searchable = BooleanField("Searchable")

class DashboardForm(Form):
    username = StringField('Display Name', [validators.InputRequired(message="You need a username."), validators.Length(min=3, max=20, message ="Usernames can be between 3 and 20 characters."), validators.Regexp(r'^[\w_-]+$', message='Usernames can only contain letters, numbers, "-" and "_".')])
    email = StringField('Email', [validators.Optional(strip_whitespace=False), validators.Email()])
    bio = StringField('Bio', [validators.Length(max=140)], widget=TextArea())
    avatar = IntegerField('Avatar')
    favorite_sub_1 = StringField('Favorite Sub 1', [validators.InputRequired(message="We need at least on favorite sub to find matches.")])
    favorite_sub_2 = StringField('Favorite Sub 2', [validators.Optional()])
    favorite_sub_3 = StringField('Favorite Sub 3', [validators.Optional()])

    age = IntegerField('Age', [validators.Optional(), validators.NumberRange(min=18, max=130, message="You must be 18 years or older.")])
    gender =  SelectField('Gender', coerce=int, validators = [validators.Optional()], choices=[(1,'Man'), (2,'Woman'), (3,'Transgender')])
    desired_gender =  SelectField('Desired Gender', coerce=int, validators = [validators.Optional()], choices=[(1,'Man'), (2,'Woman'), (3,'Transgender')])
    radius = IntegerField('Radius', widget=HiddenInput(), validators = [validators.NumberRange(min=5, max=101)])
    min_age = IntegerField('Minimum Age', widget=HiddenInput(), validators = [validators.Optional(), validators.NumberRange(min=18, max=130)])
    max_age = IntegerField('Max Age', widget=HiddenInput(), validators = [validators.Optional(), validators.NumberRange(min=18, max=130)])
    searchable = BooleanField("Searchable")

    def validate(self):
        has_error = False

        rv = Form.validate(self)
        if not rv:
            return False

        user = models.User.query.filter(func.lower(models.User.username) == func.lower(self.username.data)).first()

        # if username is taken
        if user is not None:
            # if username isn't taken by current user
            print current_user.username.lower()
            print user.username.lower()

            if current_user.username is not user.username:
                self.username.errors.append('Username not available.')

                return False

        email_user = models.User.query.filter(func.lower(models.User.email) == func.lower(self.email.data)).first()

        # if email is taken by a user
        if email_user is not None:

            # if email isn't taken by current user
            if current_user.email is not email_user.email:
                self.email.errors.append('An account with that email already exists.')
                return False

        # check if subreddits exist
        favorite_subs = []
        favorite_subs.append(self.favorite_sub_1.data)

        if self.favorite_sub_2.data:
            favorite_subs.append(self.favorite_sub_2.data)

        if self.favorite_sub_3.data:
            favorite_subs.append(self.favorite_sub_3.data)

        for sub in favorite_subs:

            # strip /r/ from name
            if '/' in sub:
                sub = sub.split('/')[-1]


            # if subreddit isn't found in reddimatch db
            if models.Subreddit.query.filter_by(name = sub).first() is None:
                r = praw_instance()
                try:
                    r.get_subreddit(sub, fetch=True)
                except Exception as e:
                    index = favorite_subs.index(sub)

                    if index is 0:
                        favorite_sub = self.favorite_sub_1
                    if index is 1:
                        favorite_sub = self.favorite_sub_2
                    if index is 2:
                        favorite_sub = self.favorite_sub_3

                    favorite_sub.errors.append("We couldn't find that subreddit. Are you sure it's spelled correctly?")

                    return False

        self.user = user
        return True

    def update_user(self):
        pass
