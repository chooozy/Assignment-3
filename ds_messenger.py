# NAME: Cameron Chen
# EMAIL: camerm3@uci.edu
# STUDENT ID: 49753193
"""Messenger client to handle DSP socket communication and message formatting."""

import socket
import time
from ds_protocol import (
    create_auth_message,
    create_direct_message,
    create_fetch_message,
    extract_json
)


class DirectMessage:
    """Simple structure to represent a direct message."""

    def __init__(self):
        """Initialize message with default empty fields."""
        self.recipient = None
        self.message = None
        self.sender = None
        self.timestamp = None

    def __str__(self):
        """Returns a formatted string representation of the message."""
        sender = self.sender or "You"
        recipient = self.recipient or "You"
        return f"[{self.timestamp}] {sender} → {recipient}: {self.message}"

    def is_valid(self) -> bool:
        """Checks if message has content and recipient."""
        return bool(self.message and self.recipient)


class DirectMessenger:
    """Handles connection, authentication, sending, and receiving messages over DSP."""

    def __init__(self, dsuserver=None, username=None, password=None):
        """Initializes DirectMessenger and attempts authentication."""
        self.dsuserver = dsuserver or '127.0.0.1'
        self.port = 3001
        self.username = username
        self.password = password
        self.token = None
        self.authenticated = self._authenticate()

    def _authenticate(self) -> bool:
        """Attempts to authenticate the user with the DSP server."""
        try:
            with socket.create_connection((self.dsuserver, self.port)) as client:
                send = client.makefile('w')
                recv = client.makefile('r')
                auth_msg = create_auth_message(self.username, self.password)
                send.write(auth_msg + '\r\n')
                send.flush()

                resp = extract_json(recv.readline())
                if resp.type == 'ok':
                    self.token = resp.token
                    return True
        except (OSError, socket.error) as e:
            print(f"Authentication failed: {e}")
        return False

    def send(self, message: str, recipient: str) -> bool:
        """Sends a message to the specified recipient.

        Args:
            message (str): The content of the message.
            recipient (str): The username of the recipient.

        Returns:
            bool: True if the message was successfully sent, False otherwise.
        """
        if not self.authenticated:
            return False  # Offline mode: cannot send

        try:
            client = socket.create_connection((self.dsuserver, self.port))
            send = client.makefile('w')
            recv = client.makefile('r')

            # Authenticate and get a fresh token
            auth_msg = create_auth_message(self.username, self.password)
            send.write(auth_msg + '\r\n')
            send.flush()
            auth_resp = extract_json(recv.readline())
            if auth_resp.type != 'ok':
                return False
            token = auth_resp.token

            # Send the direct message
            msg = create_direct_message(token, message, recipient, time.time())
            send.write(msg + '\r\n')
            send.flush()
            resp = extract_json(recv.readline())
            client.close()

            return resp.type == 'ok'
        except (OSError, socket.error) as e:
            print(f"Send failed: {e}")
            return False

    def _retrieve(self, fetch_type: str) -> list:
        """Fetches messages from the server of a given type (all/unread).

        Args:
            fetch_type (str): Type of messages to fetch ("all" or "unread").

        Returns:
            list: List of DirectMessage objects.
        """
        if not self.authenticated:
            return []  # Offline mode: no messages to retrieve

        messages = []

        try:
            client = socket.create_connection((self.dsuserver, self.port))
            send = client.makefile('w')
            recv = client.makefile('r')

            # Authenticate and get a fresh token
            auth_msg = create_auth_message(self.username, self.password)
            send.write(auth_msg + '\r\n')
            send.flush()
            auth_resp = extract_json(recv.readline())
            if auth_resp.type != 'ok':
                return messages
            token = auth_resp.token

            # Send fetch request
            fetch_msg = create_fetch_message(token, fetch_type)
            send.write(fetch_msg + '\r\n')
            send.flush()
            resp = extract_json(recv.readline())
            client.close()

            if resp.type == 'ok' and resp.messages:
                for msg in resp.messages:
                    dm = DirectMessage()
                    dm.message = msg.get("message")
                    dm.timestamp = msg.get("timestamp")
                    dm.sender = msg.get("from")
                    dm.recipient = msg.get("recipient")
                    messages.append(dm)

            return messages
        except (OSError, socket.error) as e:
            print(f"Retrieve failed: {e}")
            return []

    def retrieve_new(self) -> list:
        """Fetches only unread messages."""
        return self._retrieve("unread")

    def retrieve_all(self) -> list:
        """Fetches all available messages."""
        return self._retrieve("all")
