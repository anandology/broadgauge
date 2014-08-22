"""Actions triggered on various signals.
"""
from . import signals
from .sendmail import sendmail_with_template

@signals.trainer_signup.connect
def trainer_welcome_email(trainer):
    sendmail_with_template("emails/trainers/welcome.html",
        subject="Welcome to Python Express",
        to=trainer.email,
        trainer=trainer)

@signals.org_signup.connect
def org_welcome_email(org):
    print "new org"


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
