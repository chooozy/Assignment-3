# NAME: Cameron Chen
# EMAIL: camerm3@uci.edu
# STUDENT ID: 49753193

"""GUI for ICS32 Social Messenger App."""

import os
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from notebook import Notebook, Diary
from ds_messenger import DirectMessenger


class SocialMessengerApp:
    """Main GUI class for managing user interaction in the messenger app."""

    # pylint: disable=too-many-instance-attributes
    def __init__(self, tk_root):
        """Initialize the GUI and attempt server connection."""
        self.root = tk_root
        self.root.withdraw()  # Hide main window during login

        self.username = simpledialog.askstring("Login", "Enter your username:")
        self.password = simpledialog.askstring("Login", "Enter your password:", show="*")

        if not self.username or not self.password:
            messagebox.showerror("Login Failed", "Username and password cannot be empty.")
            self.root.destroy()
            return

        self.root.deiconify()  # Show main window again AFTER login
        self.root.title("ICS32 Social Messenger")
        self.root.geometry("800x500")

        self.notebook_path = f"{self.username}.json"
        self.notebook = Notebook(self.username, self.password, "GUI user")

        # Try to connect to the server
        try:
            self.messenger = DirectMessenger(
                dsuserver='127.0.0.1',
                username=self.username,
                password=self.password
            )
            if not self.messenger.authenticated:
                raise OSError("Authentication failed")
        except OSError as auth_error:
            messagebox.showwarning(
                "Offline Mode",
                f"Unable to connect or authenticate. Entering Offline mode.\n{auth_error}"
            )
            self.messenger = None

        # Try to load existing notebook if not create a new one
        if os.path.exists(self.notebook_path):
            try:
                self.notebook.load(self.notebook_path)
            except OSError as e:
                messagebox.showwarning("Notebook", f"Failed to load previous notebook. Error: {e}")
        else:
            self.notebook.save(self.notebook_path)  # Save new notebook on first run

        self.setup_ui()
        self.update_messages_loop()

    def setup_ui(self):
        """Create UI elements."""
        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)

        self.user_label = tk.Label(
            self.container,
            text=f"Logged in as: {self.username}",
            font=("Arial", 10, "italic")
        )
        self.user_label.pack(side="top", anchor="w", padx=10, pady=2)

        self.contact_list = ttk.Treeview(self.container)
        self.contact_list.heading("#0", text="Contacts")
        self.contact_list.bind("<<TreeviewSelect>>", self.display_conversation)
        self.contact_list.pack(side="left", fill="y")

        self.right_frame = tk.Frame(self.container)
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.message_display = tk.Text(self.right_frame, state="disabled", wrap="word")
        self.message_display.pack(fill="both", expand=True)

        self.message_input = tk.Entry(self.right_frame)
        self.message_input.pack(fill="x", padx=5, pady=5)

        self.button_frame = tk.Frame(self.right_frame)
        self.button_frame.pack(fill="x")

        self.send_button = tk.Button(self.button_frame, text="Send", command=self.send_message)
        self.send_button.pack(side="right", padx=5)

        self.add_user_button = tk.Button(self.button_frame, text="Add User", command=self.add_user)
        self.add_user_button.pack(side="left", padx=5)

        self.load_contacts()

    def load_contacts(self):
        """Load contacts from notebook into the contact list UI."""
        for contact in self.notebook.contacts:
            self.contact_list.insert("", "end", iid=contact, text=contact)

    def add_user(self):
        """Prompt to add a new contact and save to notebook."""
        new_user = simpledialog.askstring("Add Contact", "Enter username:")
        if new_user and new_user not in self.notebook.contacts:
            self.notebook.contacts.append(new_user)
            self.contact_list.insert("", "end", iid=new_user, text=new_user)
            self.notebook.save(self.notebook_path)

    def send_message(self):
        """Send a message to the selected contact."""
        selected = self.contact_list.selection()
        if not selected:
            messagebox.showinfo("No contact selected", "Please select a contact first.")
            return

        recipient = selected[0]
        message = self.message_input.get()
        if not message:
            return

        success = self.messenger.send(message, recipient) if self.messenger else False
        if success:
            entry = f"You → {recipient}: {message}"
            diary = Diary(entry=entry, timestamp=time.time())
            self.notebook.add_diary(diary)
            self.notebook.save(self.notebook_path)
            self.message_input.delete(0, tk.END)
            self.display_conversation()
        else:
            messagebox.showerror("Send Failed", "Offline... could not send the message.")

    def display_conversation(self, _event=None):
        """Display conversation with the selected contact."""
        selected = self.contact_list.selection()
        if not selected:
            return

        user = selected[0]
        self.message_display.config(state="normal")
        self.message_display.delete(1.0, tk.END)

        self.message_display.tag_config("name", font=("Arial", 10, "bold"))
        self.message_display.tag_config("timestamp", foreground="gray")

        for d in self.notebook.get_diaries():
            if f"→ {user}:" in d.entry or f"{user} →" in d.entry:
                ts = datetime.fromtimestamp(d.timestamp).strftime('%H:%M')
                self.message_display.insert(tk.END, f"{ts} ", "timestamp")

                if "→" in d.entry:
                    sender = d.entry.split("→")[0].strip()
                    msg = d.entry.split(":", 1)[1].strip()
                    self.message_display.insert(tk.END, f"{sender}: ", "name")
                    self.message_display.insert(tk.END, f"{msg}\n")
                else:
                    self.message_display.insert(tk.END, f"{d.entry}\n")

        self.message_display.config(state="disabled")

    def update_messages_loop(self):
        """Periodically check and retrieve new messages."""
        if self.messenger:
            new_messages = self.messenger.retrieve_new()
            for m in new_messages:
                entry = f"{m.sender} → You: {m.message}"
                diary = Diary(entry=entry, timestamp=float(m.timestamp))
                self.notebook.add_diary(diary)
                if m.sender not in self.notebook.contacts:
                    self.notebook.contacts.append(m.sender)
                    self.contact_list.insert("", "end", iid=m.sender, text=m.sender)
            self.notebook.save(self.notebook_path)

        self.display_conversation()
        self.root.after(5000, self.update_messages_loop)  # Check every 5 seconds


if __name__ == '__main__':
    TK_ROOT = tk.Tk()
    app = SocialMessengerApp(TK_ROOT)
    TK_ROOT.mainloop()
