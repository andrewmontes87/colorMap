# -*- coding: utf8 -*-
from flask_wtf import FlaskForm 
from wtforms import StringField, HiddenField, PasswordField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, EqualTo, Email, Length

class UploadForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired("Please enter a note title")])
    submit = SubmitField("Upload")
