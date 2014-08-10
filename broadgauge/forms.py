"""Forms using WTF-forms.
"""
import web
from wtforms import (
    Form,
    BooleanField, DateField, IntegerField, 
    StringField, TextAreaField,
    validators)

from .models import User

class MultiDict(web.storage):
    """wtforms expect the formdate to be a multi-dict instance with getall method.
    This is a hack to make it work with web.py apps.
    """
    def getall(self, name):
        if name in self:
            return [self[name]]
        else:
            return []


class BaseForm(Form):
    def __init__(self, formdata=None, **kwargs):
        formdata = formdata and MultiDict(formdata) or None
        Form.__init__(self, formdata, **kwargs)


class TrainerSignupForm(BaseForm):
    name = StringField('Name', [validators.Required()])
    phone = StringField('Phone', [validators.Required()])
    city = StringField('City', [validators.Required()])
    # No need to have email as it is alreday available from session


class OrganizationSignupForm(BaseForm):
    name = StringField('Name', [validators.Required()])
    city = StringField('City', [validators.Required()])
    role = StringField('Role', [validators.Required()])

class TrainerEditProfileForm(BaseForm):
    name = StringField('Name', [validators.Required()])
    phone = StringField('Phone', [validators.Required()])
    city = StringField('City', [validators.Required()])
    website = StringField('Website', [])
    bio = TextAreaField('Bio', [])

class NewWorkshopForm(BaseForm):
    title = StringField('Title', [validators.Required()])
    description = TextAreaField('Description', [validators.Required()])
    expected_participants = IntegerField('Expected number of pariticipants', [validators.Required()])
    preferred_date = DateField('Preferred Date', [validators.Required()])

class AdminAddOrgForm(BaseForm):
    name = StringField('Name', [validators.Required()])
    city = StringField('City', [validators.Required()])

class AdminAddPersonForm(BaseForm):
    name = StringField('Name', [validators.Required()])
    email = StringField('E-mail Address', [validators.Required(), validators.Email()])
    phone = StringField('Phone Number', [validators.Required()])
    city = StringField('City', [validators.Required()])
    trainer = BooleanField('Is He/She a Trainer?')

def valid_user_email(form, field):
    email = field.data
    if not User.find(email=email):
        raise validators.ValidationError("No user found with that email address.")

class OrgAddMemberForm(BaseForm):
    email = StringField('E-mail Address', [validators.Required(), valid_user_email])
    role = StringField('Role', [validators.Required()])