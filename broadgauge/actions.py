"""Actions triggered on various signals.
"""
import web
from . import account, signals
from .sendmail import sendmail_with_template
from .models import Activity

def record_activity(name, info):
    user = account.get_current_user()
    Activity.new(name, user, info)

@signals.trainer_signup.connect
def activity_trainer_signup(trainer):
    record_activity('trainer-signup', trainer.dict())

@signals.org_signup.connect
def activity_org_signup(org):
    record_activity('org-signup', org.dict())

@signals.new_workshop.connect
def activity_new_workshop(workshop):
    record_activity('new-workshop', workshop.dict())

@signals.workshop_express_interest.connect
def activity_express_interest(workshop, trainer):
    record_activity('workshop-express-interest', dict(
        workshop=workshop.dict(),
        trainer=trainer.dict()))

@signals.workshop_withdraw_interest.connect
def activity_withdraw_interest(workshop, trainer):
    record_activity('workshop-withdraw-interest', dict(
        workshop=workshop.dict(),
        trainer=trainer.dict()))

@signals.workshop_confirmed.connect
def activity_workshop_confirmed(workshop, trainer):
    record_activity('workshop-confirmed', dict(
        workshop=workshop.dict(),
        trainer=trainer.dict()))

@signals.workshop_confirmed.connect
def on_workshop_confirmed(workshop, trainer):
    member_emails = [m.email for m, role in workshop.get_members()]
    sendmail_with_template("emails/workshop_confirmed.html",
        subject="{} workshop is confirmed".format(workshop['title']),
        to=[trainer.email] + member_emails,
        cc=web.config.get('contact_email'),
        workshop=workshop,
        trainer=trainer)

@signals.trainer_signup.connect
def trainer_welcome_email(trainer):
    sendmail_with_template("emails/trainers/welcome.html",
        subject="Welcome to Python Express",
        to=trainer.email,
        trainer=trainer)


@signals.org_signup.connect
def org_welcome_email(org):
    pass


@signals.new_workshop.connect
def on_new_workshop(org):
    pass

@signals.new_comment.connect
def on_new_comment(comment):
    workshop = comment.get_workshop()
    subject = "New comment on {}".format(workshop.title)
    for u in workshop.get_followers():
        sendmail_with_template("emails/comment-added.html",
            to=u.email,
            subject=subject,
            workshop=workshop,
            user=u,
            comment=comment)