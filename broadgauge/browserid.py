import web
import json
import requests

def verify_assertion(assertion):
    """Expects BROWSERID_AUDIENCE in the config.
    """
    payload = {
        "assertion": assertion,
        "audience": web.config.BROWSERID_AUDIENCE
    }
    response = requests.post('https://verifier.login.persona.org/verify', data=payload, verify=True)
    if response.ok:
        # Parse the response
        user_data = json.loads(response.content)

        # Check if the assertion was valid
        if user_data['status'] == 'okay':
            return user_data['email']
