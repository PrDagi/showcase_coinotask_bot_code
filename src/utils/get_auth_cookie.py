from json import load
from random import choice

def get_auth_cookie() -> dict:
    """
    Retrieve a randomly chosen authentication cookie from the 'x_bot_cookies.json' file.

    Returns:
        dict: A randomly chosen authentication cookie containing bot_id, authorization, cookie, and x-csrf-token.
    """
    with open("data/state_data/x_bot_cookies.json") as bot_cookies_file:
        bot_cookies = load(bot_cookies_file)
        return choice(bot_cookies)