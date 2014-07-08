"""Utility to display flash messages.

To add a flash message:

    flash('Login successful!', category='info')

To display flash messages in a template:

    $ for flash in get_flashed_messages():
        <div class="$flash.type">$flash.message</div>

Note: This should be added with web.py or become an independent module.
"""

import json
import web


def get_flashed_messages():
    flashes = web.ctx.get('flashes', [])
    web.ctx.flashes = []
    return flashes


def flash(message, category="info"):
    flashes = web.ctx.setdefault('flashes', [])
    flashes.append(web.storage(category=category, message=message))


def flash_processor(handler):
    flashes_json = web.cookies(flashes="[]").flashes
    try:
        flashes = [web.storage(d) for d in json.loads(flashes_json)
                   if isinstance(d, dict) and 'category' in d and
                   'message' in d]
    except ValueError:
        flashes = []

    web.ctx.flashes = list(flashes)

    try:
        return handler()
    finally:
        # Flash changed. Need to save it.
        if flashes != web.ctx.flashes:
            if web.ctx.flashes:
                web.setcookie('flashes', json.dumps(web.ctx.flashes))
            else:
                web.setcookie('flashes', '', expires=-1)
