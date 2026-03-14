
class User:
    registration = {
        'user1': {"login_name": "pr", "password": "pr123"},
        'user2': {'login_name': "rj", "password": "rj123"},
        'user3': {'login_name': "rav", "password": "rav123"},
    }

    def __init__ (self, username):
        self.username = username

    def __call__ (self):
        print (f"welcome to the App {self.username}")

    def check_username(self):
        for user in self.registration:
            if self.username == self.registration[user]["login_name"]:
                return True
            else:
                continue
        return None

    def check_password(self, password):
        for user in self.registration:
            if self.username == self.registration[user]["login_name"]:
                # Check the password
                if password == self.registration[user]["password"]:
                    return True
                else:
                    return False

    def login(self):
        if self.check_username():
            password = input("Enter Password:")
            if self.check_password(password):
                print("Login Successful")
            else:
                print("Login Failed")
        else:
            print("user does not exist")

username = input("Enter Username:")

obj1 = User(username)
print ( obj1 )
print (obj1.username)

username = input("Enter Username:")

obj2 = User(username)
obj2()
obj2.login()