import random
import hmac
import web
import datetime, time

def get_secret_key():
    return web.config.secret_key

def generate_salted_hash(text, salt=None):
    secret_key = get_secret_key()
    salt = salt or hmac.HMAC(secret_key, str(random.random())).hexdigest()[:5]
    hash = hmac.HMAC(secret_key, web.utf8(salt) + web.utf8(text)).hexdigest()
    return '%s$%s' % (salt, hash)

def check_salted_hash(text, salted_hash):
    if salted_hash and '$' in salted_hash:
        salt, hash = salted_hash.split('$', 1)
        return generate_salted_hash(text, salt) == salted_hash
    else:
        return False

def set_login_cookie(email):
    t = datetime.datetime(*time.gmtime()[:6]).isoformat()
    text = "%s,%s" % (email, t)
    text += "," + generate_salted_hash(text)
    web.setcookie("session", text)

def logout():
    web.setcookie("session", "", expires=-1)

def get_current_user():
    if "current_user" not in web.ctx:
        web.ctx.current_user = _get_current_user()
    return web.ctx.current_user

def _get_current_user():
    session = web.cookies(session="").session
    try:
        email, login_time, digest = session.split(',')
    except ValueError:
        return

    if check_salted_hash(email + "," + login_time, digest):
        return email
