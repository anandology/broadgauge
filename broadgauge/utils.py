import web

def setup_error_emails(app):
    if "smtp_server" in web.config and "bug_master" in web.config:
        app.internalerror = web.emailerrors(
            web.config.bug_master,
            app.internalerror,
            web.config.from_address)
