# a2.py

# Starter code for assignment 2 in ICS 32 Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# Cameron Chen
# camermc3@uci.edu
# 49753193

# a3.py
from ds_messenger import DirectMessenger
from notebook import Notebook, Diary
import os
import time

def main():
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    # Notebook setup
    notebook_path = f"{username}.json"
    notebook = Notebook(username=username, password=password, bio="Default bio")
    if os.path.exists(notebook_path):
        try:
            notebook.load(notebook_path)
            print(f"Loaded notebook with {len(notebook.get_diaries())} messages and {len(notebook.contacts)} contacts.")
        except:
            print("Failed to load notebook.")
    else:
        print("New notebook created.")

    # Connect to server
    messenger = DirectMessenger(username=username, password=password)

    if not messenger.authenticated:
        print("Failed to authenticate.")
        return

    while True:
        print("\n1. Send Message\n2. Fetch New\n3. Fetch All\n4. Exit")
        choice = input("Select: ")
        if choice == "1":
            recipient = input("To: ")
            msg = input("Message: ")
            if messenger.send(msg, recipient):
                print("Message sent!")

                # Save to notebook
                entry = f"You → {recipient}: {msg}"
                diary = Diary(entry=entry, timestamp=time.time())
                notebook.add_diary(diary)
                if recipient not in notebook.contacts:
                    notebook.contacts.append(recipient)
                notebook.save(notebook_path)
            else:
                print("Send failed.")

        elif choice == "2":
            msgs = messenger.retrieve_new()
            for m in msgs:
                print(f"[NEW] {m.sender}: {m.message}")

                # Save to notebook
                entry = f"{m.sender} → You: {m.message}"
                diary = Diary(entry=entry, timestamp=float(m.timestamp))
                notebook.add_diary(diary)
                if m.sender not in notebook.contacts:
                    notebook.contacts.append(m.sender)
            notebook.save(notebook_path)

        elif choice == "3":
            msgs = messenger.retrieve_all()
            for m in msgs:
                if m.sender:
                    print(f"{m.sender} → you: {m.message}")
                    entry = f"{m.sender} → You: {m.message}"
                    name = m.sender
                elif m.recipient:
                    print(f"you → {m.recipient}: {m.message}")
                    entry = f"You → {m.recipient}: {m.message}"
                    name = m.recipient
                else:
                    continue

                # Save to notebook
                diary = Diary(entry=entry, timestamp=float(m.timestamp))
                notebook.add_diary(diary)
                if name and name not in notebook.contacts:
                    notebook.contacts.append(name)
            notebook.save(notebook_path)

        elif choice == "4":
            break

if __name__ == '__main__':
    main()
