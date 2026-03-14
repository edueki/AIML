from db import cursor, cnx

class UserSignup:
    def create_user(self, username, password, email):
        cursor.execute("INSERT INTO signup (username, password, email) VALUES (%s, %s, %s)",
                       (username, password, email)
        )
        cnx.commit()
        print ("User created successfully")


