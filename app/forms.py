from wtforms import Form, BooleanField, StringField, PasswordField, validators, IntegerField, SelectField

class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    age = IntegerField('Age')
    gender = SelectField(choices=[('male', 'Male'), ('female', 'Female')])
    location = StringField('Location', [validators.Length(min=6, max=35)])
    bio = StringField('Bio', [validators.Length(min=0, max=140)])
