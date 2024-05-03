from urllib.parse import quote
import json


def encode_url_query(query_value: dict) -> str:
    """
    Encode a dictionary into a URL-safe query string.

    Parameters:
        query_value (dict): A dictionary containing the query parameters to be encoded.

    Returns:
        str: The URL-safe encoded query string.

    Example:
        >>> encode_url_query({'key1': 'value1', 'key2': 'value2'})
    """
    q_str = json.dumps(query_value).replace(" ", "")
    encoded_q = quote(q_str)
    
    return encoded_q