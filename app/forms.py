from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField
from wtforms.validators import DataRequired, Email

class NewsletterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    preferences = StringField('Preferences', validators=[DataRequired()])
    submit = SubmitField('Subscribe')
class ScrapeForm(FlaskForm):
    urls = TextAreaField('Enter URLs (comma-separated)', validators=[DataRequired()])
    submit = SubmitField('Scrape and Summarize')
