from envelopes import Envelope

from .template import render_template
import default_settings

def sendmail(template, **kwargs):
    """
    Sends an email with the selected html template.
    html templates can be found inside the broadguage/templates
    directory. 

    Params:
    =======
    template: str
    Link to the html file to be used as template. The html
    file is parsed by Jinja Templating before sending to the
    recipient. 

    Keyword Args:
    =============
    to: str
    Recipient's email
    
    sub: str
    Subject of the mail

    P.S: Other keywords are sent to Jinja Templating Language for 
    direct parsing, as it is.
    
    Example:
    >>> from sendmail import sendmail
    >>> sendmail("emails/trainers/welcome.html",to=..."some_email.com", 
                               sub="Hey Friend!", variable1=var, variable2=var2)
    Email sent to some_email.com
    """
    
    envelope = Envelope(
        from_addr=default_settings.from_email,
        to_addr=kwargs.pop('to'),
        subject=kwargs.pop('subject'),
        html_body=render_template(template, **kwargs)
    )
    result = envelope.send(default_settings.smtp, **default_settings.smtp_credentials)
    return result