from aiohttp import ClientSession
from random import uniform, choice
from time import sleep
from typing import Union


async def get_user_id(username: str) -> Union[str, None]:
    """
    Retrieves the user ID associated with a given Twitter username.

    Args:
        username (str): The Twitter username for which to retrieve the ID.

    Returns:
        Union[str, None]: The user ID if found, otherwise None.

    Note:
        This function tries multiple APIs to retrieve the user ID and returns
        it if found. It tries a maximum of three times with random delays
        between requests.

    Example:
        >>> get_user_id("elonmusk")
        '34713362'
    """
    tried = 0
    API_URLS = [
        "https://vackao.supportapp.cloud/v1/api/twitter/{username}",
        "https://twitvd.com/twuserid.php?username={username}"
    ]

    while tried < 3:
        # Send the request to the URLs (randomly picked)
        url = choice(API_URLS).format(username=username)
        try:
            async with ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        json_res = await response.json()

                        # Check if the username is correct and it really exists
                        is_correct_username = json_res.get("success") or json_res.get("sc")
                        if is_correct_username:

                            # Get data node that contains user id
                            res_data = json_res["data"]
                            # It could be in id or user_id attribute from the two URLs
                            user_id = res_data.get("user_id") or res_data.get("id")
                            return user_id
                        else:
                            return None
                    else:
                        response.raise_for_status()
        except Exception:
            pass
        tried += 1
        # Sleep on each try and request
        sleep(uniform(0.3, 1.3))