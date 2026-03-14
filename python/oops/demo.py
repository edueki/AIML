# Classes
# Objects

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

class RegularUser(UserBase):
    pass

class PremiumUser(UserBase):
    def __init__(self, username, msg):
        self.msg = msg
        super().__init__(username)

    def user_validation(self):
        for user in self.registration:
            if self.username == self.registration[user]["login_name"]:
                return True
            else:
                continue
        return None

    def password_validation(self):
        max_attempts = 3
        failed_attempts = 0
        while failed_attempts < max_attempts:
            password = input("Enter your password: ")
            password_match = False
            for user in self.registration:
                if self.username == self.registration[user]["login_name"]:
                    if password == self.registration[user]["password"]:
                        print("Password match")
                        password_match = True
                        break
                    else:
                        print("Password doesn't match")
            if password_match:
                break
            failed_attempts = failed_attempts + 1
            if failed_attempts < max_attempts:
                continue
            else:
                print("You have reached the maximum number of attempts")
                break

pr_obj = PremiumUser("pr", "This is  my welcome msg")
# ar_obj = PremiumUser("ar")
# rj_obj = PremiumUser("rj")

# pr_obj()
pr_obj.display_user()

# if pr_obj.user_validation():
#     print (f"username: {pr_obj.username} found")
# if ar_obj.user_validation():
#     print(f"username: {ar_obj.username} found")
# if rj_obj.user_validation():
#     print(f"username: {rj_obj.username} found")

#pr_obj.password_validation()
#ar_obj.password_validation()
#rj_obj.password_validation()


# print (obj1)
# print (obj1.registration)
# obj1.user_validation("pr")
#
# obj2 = User()
# obj2.user_validation("ar")
# print (obj2.registration)
#print (obj1)
#print (obj2)
