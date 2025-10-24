# NAME: Cameron Chen
# EMAIL: camerm3@uci.edu
# STUDENT ID: 49753193

"""Module for managing diary entries and user notebooks for ICS 32 Assignment 1."""

# ICS 32
# Assignment #1: Diary
#
# Author: Aaron Imani
#
# v0.1.0
#
# Cameron Chen
# camermc3@uci.edu
# 49753193

import json
import time
from pathlib import Path


class NotebookFileError(Exception):
    """Raised when there is an error saving or loading a notebook file."""


class IncorrectNotebookError(Exception):
    """Raised when deserialization of a notebook fails."""


class Diary(dict):
    """
    The Diary class handles individual user diary entries.

    It manages timestamp and entry data, and exposes them as properties
    that update automatically when set.
    """

    def __init__(self, entry: str = None, timestamp: float = 0):
        self._timestamp = timestamp
        self.set_entry(entry)
        dict.__init__(self, entry=self._entry, timestamp=self._timestamp)

    def set_entry(self, entry):
        """
        Sets the diary entry and updates timestamp if not already set.
        """
        self._entry = entry
        dict.__setitem__(self, 'entry', entry)

        if self._timestamp == 0:
            self._timestamp = time.time()

    def get_entry(self):
        """
        Returns the diary entry string.
        """
        return self._entry

    def set_time(self, timestamp: float):
        """
        Sets the diary timestamp.
        """
        self._timestamp = timestamp
        dict.__setitem__(self, 'timestamp', timestamp)

    def get_time(self):
        """
        Returns the diary timestamp.
        """
        return self._timestamp

    # Properties for timestamp and entry
    entry = property(get_entry, set_entry)
    timestamp = property(get_time, set_time)


class Notebook:
    """
    The Notebook class stores user profile info and diary entries.
    """

    def __init__(self, username: str, password: str, bio: str):
        """
        Creates a new Notebook object.

        Args:
            username (str): The username of the user.
            password (str): The password of the user.
            bio (str): The bio of the user.
        """
        self.username = username
        self.password = password
        self.bio = bio
        self._diaries = []
        self.contacts = []

    def add_diary(self, diary: Diary) -> None:
        """
        Adds a Diary object to the list of diaries.
        """
        self._diaries.append(diary)

    def del_diary(self, index: int) -> bool:
        """
        Removes a Diary at the given index.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            del self._diaries[index]
            return True
        except IndexError:
            return False

    def get_diaries(self) -> list[Diary]:
        """
        Returns the list of all diary entries.

        Returns:
            list[Diary]: The list of Diary objects.
        """
        return self._diaries

    def save(self, path: str) -> None:
        """
        Saves the Notebook instance to a JSON file.

        Args:
            path (str): Path to save the JSON file.

        Raises:
            NotebookFileError: If the file extension is not .json.
        """
        p = Path(path)

        if p.suffix == '.json':
            with open(p, 'w', encoding='utf-8') as f:
                json.dump({
                    'username': self.username,
                    'password': self.password,
                    'bio': self.bio,
                    'contacts': self.contacts,
                    '_diaries': [d.__dict__ for d in self._diaries]
                }, f, indent=4)
        else:
            raise NotebookFileError("Invalid notebook file path or type")

    def load(self, filepath: str):
        """
        Loads the Notebook data from JSON file.

        Args:
            filepath (str): Path to the notebook file.

        Raises:
            IncorrectNotebookError: If the notebook file is corrupted or invalid.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.username = data['username']
                self.password = data['password']
                self.bio = data['bio']
                self.contacts = data['contacts']
                self._diaries = []

                for diary in data.get('_diaries', []):
                    self._diaries.append(Diary(diary['_entry'], diary['_timestamp']))
        except Exception as e:
            print("Error loading notebook:", e)
            raise IncorrectNotebookError("Failed to load notebook.") from e
