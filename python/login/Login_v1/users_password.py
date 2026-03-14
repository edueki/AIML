from login_base import PasswordBase

class Password(PasswordBase):
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