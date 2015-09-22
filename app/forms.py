from wtforms import Form, BooleanField, StringField, PasswordField, validators, IntegerField, SelectField

class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    age = IntegerField('Age')
    gender = SelectField(choices=[('male', 'Male'), ('female', 'Female')])
    location = StringField('Location', [validators.Length(min=6, max=35)])
    bio = StringField('Bio', [validators.Length(min=0, max=140)])
    favorite_sub_1 = StringField('Favorite Sub 1', [validators.Length(min=1, max=30)])
    favorite_sub_2 = StringField('Favorite Sub 2', [validators.Length(min=1, max=30)])
    favorite_sub_3 = StringField('Favorite Sub 3', [validators.Length(min=1, max=30)])
