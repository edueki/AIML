class UserBase:
    def __init__(self, username):
        self.username = username
        self.registration = {
        "user1": {"login_name": "pr", "password": "1234"},
        "user2": {"login_name": "ar", "password": "4567"},
        "user3": {"login_name": "rj", "password": "5678"},
        }
    def __call__(self):
        print (f"Welcome {self.username}!")

    def display_user(self):
        print(f"this is from base class: {self.username}")
class PasswordBase:
    def __init__(self, username):
        self.username = username
        self.registration = {
            "user1": {"login_name": "pr", "password": "1234"},
            "user2": {"login_name": "ar", "password": "4567"},
            "user3": {"login_name": "rj", "password": "5678"},
        }
