"""Forms using WTF-forms.
"""
import web
from wtforms import (
    Form,
    BooleanField, DateField, IntegerField, 
    StringField, TextAreaField,
    SelectField,
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
    username = StringField('Username', [
        validators.Required(), 
        validators.Length(min=3),
        validators.Regexp('^[a-zA-Z0-9._-]+$', message="Only letters, numbers, dot,")])
    phone = StringField('Phone', [validators.Required()])
    city = StringField('City', [validators.Required()])
    # No need to have email as it is alreday available from session

    def valid_username(self, field):
        if User.find(username=field.data):
            raise validators.ValidationError("Username already used.")
            

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
    date = DateField('Preferred Date', [validators.Required()])

class AdminAddOrgForm(BaseForm):
    name = StringField('Name', [validators.Required()])
    city = StringField('City', [validators.Required()])

class AdminAddPersonForm(BaseForm):
    name = StringField('Name', [validators.Required()])
    email = StringField('E-mail Address', [validators.Required(), validators.Email()])
    phone = StringField('Phone Number', [validators.Required()])
    city = StringField('City', [validators.Required()])
    trainer = BooleanField('Is He/She a Trainer?')

class ValidUser:
    def __init__(self, trainer=False, admin=False):
        self.trainer = trainer
        self.admin = admin

    def __call__(self, form, field):
        email = field.data
        user = User.find(email=email)
        if not user:
            raise validators.ValidationError("No user found with that email address.")
        if self.trainer and not user.is_trainer():
            raise validators.ValidationError("User with that email is not a trainer.")
        if self.admin and not user.is_admin():
            raise validators.ValidationError("User with that email is not a admin.")


class OrgAddMemberForm(BaseForm):
    email = StringField('E-mail Address', [validators.Required(), ValidUser()])
    role = StringField('Role', [validators.Required()])


class WorkshopSetTrainerForm(BaseForm):
    email = StringField('E-mail Address', [validators.Required(), ValidUser(trainer=True)])

class ContactForm(BaseForm):
    email = StringField('Your E-mail Address', [validators.Required(), validators.Email()])
    subject = StringField('Subject', [validators.Required()])
    message = TextAreaField('Your Question', [validators.Required()])

class AdminSendmailForm(BaseForm):
    to = SelectField("Send Mail To", choices=[('self', 'To yourself'),
                                              ('trainers', 'All trainers'),
                                              ('org-members', 'Members of all organizations')])
    subject = StringField('Subject', [validators.Required()])
    body = TextAreaField('Body', [validators.Required()])
