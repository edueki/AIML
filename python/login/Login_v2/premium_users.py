from login_base import UserBase
# print (__name__)

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