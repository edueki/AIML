from login_base import UserBase
from db import cursor

class UserValidation:

    def user_validation(self, username):
        response = cursor.execute("SELECT username FROM signup WHERE USERNAME=%s", (username,))
        return cursor.fetchone() is not None


