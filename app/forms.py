from wtforms import Form, BooleanField, StringField, PasswordField, validators, IntegerField, SelectField
from wtforms.widgets import TextArea

class RegistrationForm(Form):
    username = StringField('Username', [validators.Required(), validators.Length(min=3, max=20)])
    email = StringField('Email', [validators.Email(), validators.Optional()])
    bio = StringField('Bio', [validators.Length(max=140)], widget=TextArea())
    avatar = IntegerField('Avatar')
    favorite_sub_1 = StringField('Favorite Sub 1', [validators.Required()])
    favorite_sub_2 = StringField('Favorite Sub 2', [validators.Optional()])
    favorite_sub_3 = StringField('Favorite Sub 3', [validators.Optional()])
