# NAME: Cameron Chen
# EMAIL: camerm3@uci.edu
# STUDENT ID: 49753193

"""Unit tests for ds_protocol and ds_messenger modules."""

import unittest
import json
from unittest.mock import patch, MagicMock

from ds_protocol import (
    create_auth_message,
    create_direct_message,
    create_fetch_message,
    extract_json
)
from ds_messenger import DirectMessenger, DirectMessage


class TestDSPProtocol(unittest.TestCase):
    """Tests for ds_protocol module functions."""

    def test_send_offline_mode(self):
        """Test that makes send returns False if not authenticated."""
        dm = DirectMessenger()
        dm.authenticated = False
        result = dm.send("Hello", "bob")
        self.assertFalse(result)

    def test_retrieve_new_offline_mode(self):
        """Test that retrieve_new returns an empty list when not authenticated."""
        dm = DirectMessenger()
        dm.authenticated = False
        result = dm.retrieve_new()
        self.assertEqual(result, [])

    def test_create_auth_message(self):
        """Tests the creation of an authentication message."""
        expected = json.dumps({"authenticate": {"username": "user1", "password": "pass1"}})
        result = create_auth_message("user1", "pass1")
        self.assertEqual(result, expected)

    def test_create_direct_message(self):
        """Test creation of a direct message(dm)."""
        timestamp = 1234567890.0
        expected = json.dumps({
            "token": "abc123",
            "directmessage": {
                "entry": "Hello",
                "recipient": "bob",
                "timestamp": str(timestamp)
            }
        })
        result = create_direct_message("abc123", "Hello", "bob", timestamp)
        self.assertEqual(result, expected)

    def test_create_fetch_message(self):
        """Test creation of a fetch message."""
        expected = json.dumps({"token": "abc123", "fetch": "all"})
        result = create_fetch_message("abc123", "all")
        self.assertEqual(result, expected)

    def test_extract_json_success(self):
        """Tests successful JSON extraction."""
        json_msg = json.dumps({
            "response": {
                "type": "ok",
                "message": "Success",
                "token": "abc123",
                "messages": []
            }
        })
        result = extract_json(json_msg)
        self.assertEqual(result.type, "ok")
        self.assertEqual(result.message, "Success")
        self.assertEqual(result.token, "abc123")
        self.assertEqual(result.messages, [])

    def test_extract_json_failure(self):
        """Test extract_json handles invalid JSON string."""
        result = extract_json("not a json string")
        self.assertEqual(result.type, "error")

    def test_extract_json_missing_response(self):
        """Test extract_json handles missing response key."""
        malformed_json = json.dumps({"invalid_key": {}})
        result = extract_json(malformed_json)
        self.assertEqual(result.type, "error")

    def test_extract_json_unexpected_structure(self):
        """Test extract_json handles unexpected structure."""
        weird_json = json.dumps({"response": 123})
        result = extract_json(weird_json)
        self.assertEqual(result.type, "error")

    def test_extract_json_type_error(self):
        """Test extract_json handles non-string input."""
        result = extract_json(12345)
        self.assertEqual(result.type, "error")


class TestDSMessenger(unittest.TestCase):
    """Tests for DirectMessenger class."""

    def setUp(self):
        """Set up common test variables."""
        self.username = "test_user"
        self.password = "test_pass"
        self.server = "127.0.0.1"

    @patch('ds_messenger.DirectMessenger._authenticate', return_value=False)
    def test_direct_messenger_default_init(self, _):
        """Test DirectMessenger init sets authenticated to False."""
        dm = DirectMessenger()
        self.assertFalse(dm.authenticated)

    def test_send_invalid_message(self):
        """Test send returns False with invalid recipient."""
        dm = DirectMessenger()
        dm.authenticated = True
        result = dm.send("Hello", None)
        self.assertFalse(result)

    def test_direct_message_is_valid(self):
        """Test DirectMessage is valid with proper fields."""
        msg = DirectMessage()
        msg.message = "hello"
        msg.recipient = "bob"
        self.assertTrue(msg.is_valid())
        msg.recipient = None
        self.assertFalse(msg.is_valid())

    def test_direct_message_is_invalid(self):
        """Test DirectMessage is invalid with missing fields."""
        msg = DirectMessage()
        msg.message = None
        msg.recipient = None
        self.assertFalse(msg.is_valid())

    def test_direct_message_str_defaults(self):
        """Test string output for default DirectMessage."""
        msg = DirectMessage()
        msg.message = "test"
        msg.timestamp = "00:00"
        self.assertIn("You", str(msg))

    def test_direct_message_str(self):
        """Test string output for fully set DirectMessage."""
        msg = DirectMessage()
        msg.sender = "alice"
        msg.recipient = "bob"
        msg.message = "hi"
        msg.timestamp = "1234"
        self.assertIn("alice", str(msg))
        self.assertIn("bob", str(msg))
        self.assertIn("hi", str(msg))

    def test_direct_message_defaults(self):
        """Test DirectMessage default attribute values."""
        msg = DirectMessage()
        self.assertIsNone(msg.sender)
        self.assertIsNone(msg.recipient)
        self.assertIsNone(msg.message)
        self.assertIsNone(msg.timestamp)
        self.assertFalse(msg.is_valid())

    @patch('ds_messenger.extract_json')
    @patch('socket.create_connection')
    def test_send_fails_after_authentication(self, _, mock_extract):
        """Test send returns False when server responds with error."""
        mock_response = MagicMock()
        mock_response.type = 'error'
        mock_extract.return_value = mock_response
        dm = DirectMessenger()
        dm.authenticated = True
        dm.token = "abc123"
        result = dm.send("hello", "bob")
        self.assertFalse(result)

    @patch('ds_messenger.extract_json')
    @patch('socket.create_connection')
    def test_send_fails_on_bad_token(self, _, mock_extract):
        """Test send fails with invalid token."""
        mock_resp = MagicMock()
        mock_resp.type = 'error'
        mock_extract.return_value = mock_resp
        dm = DirectMessenger()
        dm.authenticated = True
        result = dm.send("Hi", "bob")
        self.assertFalse(result)

    @patch('socket.create_connection', side_effect=OSError("Simulated failure"))
    def test_send_network_error(self, _):
        """Test send handles network errors."""
        dm = DirectMessenger()
        dm.authenticated = True
        result = dm.send("Hello", "bob")
        self.assertFalse(result)

    @patch('builtins.print')
    @patch('socket.create_connection', side_effect=OSError("Simulated send failure"))
    def test_send_print_exception(self, _, mock_print):
        """Test send prints error on network failure."""
        dm = DirectMessenger()
        dm.authenticated = True
        dm.send("Hello", "bob")
        mock_print.assert_called_with("Send failed: Simulated send failure")

    @patch('ds_messenger.extract_json')
    @patch('socket.create_connection')
    def test_retrieve_auth_fails(self, _, mock_extract):
        """Test retrieve returns empty list on auth failure."""
        mock_extract.return_value = MagicMock(type='error')
        dm = DirectMessenger()
        dm.authenticated = True
        result = dm.retrieve_new()
        self.assertEqual(result, [])

    @patch('ds_messenger.extract_json')
    @patch('socket.create_connection')
    def test_retrieve_handles_empty_messages(self, _, mock_extract):
        """Test retrieve handles None in messages field."""
        mock_response = MagicMock()
        mock_response.type = 'ok'
        mock_response.token = 'abc123'
        mock_response.messages = None
        mock_extract.return_value = mock_response
        dm = DirectMessenger()
        dm.authenticated = True
        dm.token = 'abc123'
        result = dm.retrieve_new()
        self.assertEqual(result, [])

    @patch('ds_messenger.extract_json')
    @patch('socket.create_connection')
    def test_retrieve_no_messages(self, _, mock_extract):
        """Test retrieve_all returns empty list with no messages."""
        mock_resp = MagicMock()
        mock_resp.type = 'ok'
        mock_resp.token = 'abc123'
        mock_resp.messages = []
        mock_extract.return_value = mock_resp
        dm = DirectMessenger()
        dm.authenticated = True
        dm.token = 'abc123'
        result = dm.retrieve_all()
        self.assertEqual(result, [])

    @patch('ds_messenger.extract_json')
    @patch('socket.create_connection')
    def test_retrieve_malformed_message_fields(self, _, mock_extract):
        """Test retrieve handles malformed message structure."""
        mock_resp = MagicMock()
        mock_resp.type = 'ok'
        mock_resp.token = 'abc123'
        mock_resp.messages = [{"from": "bob"}]
        mock_extract.return_value = mock_resp
        dm = DirectMessenger()
        dm.authenticated = True
        result = dm.retrieve_all()
        self.assertEqual(len(result), 1)
        self.assertIsNone(result[0].message)

    @patch('socket.create_connection', side_effect=OSError("Simulated error"))
    def test_retrieve_network_failure(self, _):
        """Test retrieve handles network failure gracefully."""
        dm = DirectMessenger()
        dm.authenticated = True
        result = dm.retrieve_all()
        self.assertEqual(result, [])

    @patch('builtins.print')
    @patch('socket.create_connection', side_effect=OSError("Simulated retrieve error"))
    def test_retrieve_print_exception(self, _, mock_print):
        """Test retrieve prints exception on error."""
        dm = DirectMessenger()
        dm.authenticated = True
        dm.retrieve_all()
        mock_print.assert_called_with("Retrieve failed: Simulated retrieve error")

    @patch('socket.create_connection')
    @patch('ds_messenger.extract_json')
    def test_authentication_failure_invalid_response(self, mock_extract, _):
        """Test authentication fails when response is not ok."""
        mock_extract.return_value = MagicMock(type='error', token=None)
        dm = DirectMessenger(dsuserver='127.0.0.1', username='user', password='pass')
        self.assertFalse(dm.authenticated)

    @patch('socket.create_connection')
    @patch('ds_messenger.extract_json')
    def test_authentication_success(self, mock_extract, _):
        """Test successful authentication sets token."""
        mock_extract.return_value = MagicMock(type='ok', token='tok123')
        dm = DirectMessenger(dsuserver='127.0.0.1', username='user', password='pass')
        self.assertTrue(dm.authenticated)
        self.assertEqual(dm.token, 'tok123')


if __name__ == '__main__':
    unittest.main()
