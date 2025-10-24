# NAME: Cameron Chen
# EMAIL: camerm3@uci.edu
# STUDENT ID: 49753193

"""DSP protocol utilities for parsing and creating JSON messages.

Supports authentication, messaging, and message retrieval.
"""

import json
from typing import Any
from collections import namedtuple

DSPResponse = namedtuple("DSPResponse", ["type", "message", "token", "messages"])


def extract_json(json_msg: str) -> DSPResponse:
    """
    Parses a JSON string from the DSP server and extracts response fields.

    Args:
        json_msg (str): The JSON string received from the server.

    Returns:
        DSPResponse: A namedtuple with fields for type, message, token, and messages.
    """
    try:
        json_obj: dict[str, Any] = json.loads(json_msg)
        response = json_obj.get("response")

        if not isinstance(response, dict):
            return DSPResponse("error", "Malformed response structure", None, [])

        return DSPResponse(
            response.get("type", "error"),
            response.get("message"),
            response.get("token"),
            response.get("messages", [])
        )

    except json.JSONDecodeError:
        return DSPResponse("error", "Invalid JSON", None, [])

    except TypeError:
        return DSPResponse("error", "Input must be a string", None, [])


def create_auth_message(username: str, password: str) -> str:
    """
    Creates a JSON string for user authentication.

    Args:
        username (str): The username of the user.
        password (str): The password of the user.

    Returns:
        str: A JSON string for the authentication message.
    """
    return json.dumps({
        "authenticate": {
            "username": username,
            "password": password
        }
    })


def create_direct_message(token: str, message: str, recipient: str, timestamp: float) -> str:
    """
    Creates a JSON string to send a direct message.

    Args:
        token (str): The user's authentication token.
        message (str): The message content.
        recipient (str): The recipient's username.
        timestamp (float): The time the message was sent.

    Returns:
        str: A JSON string representing the direct message.
    """
    return json.dumps({
        "token": token,
        "directmessage": {
            "entry": message,
            "recipient": recipient,
            "timestamp": str(timestamp)
        }
    })


def create_fetch_message(token: str, fetch_type: str) -> str:
    """
    Creates a JSON string to fetch messages.

    Args:
        token (str): The user's authentication token.
        fetch_type (str): Type of messages to fetch ("all" or "unread").

    Returns:
        str: A JSON string representing the fetch request.
    """
    return json.dumps({
        "token": token,
        "fetch": fetch_type
    })
