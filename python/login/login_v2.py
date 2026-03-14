# Login App
# Functionality
# 1. Check if the user name is found
# 2. Check if the password is correct
# 3. Max password attempts are 3

#Registration Data
# registration = {}

registration = {
    'user1': {"login_name": "pr", "password": "pr123"},
    'user2': {'login_name': "rj", "password": "rj123"},
    'user3': {'login_name': "rav", "password": "rav123"},
}
# Login Functionality
def check_username(username):
    for user in registration:
        if username == registration[user]["login_name"]:
           return True
        else:
            continue
    return None

def check_password(username, password):
    for user in registration:
        if username == registration[user]["login_name"]:
            # Check the password
            if password == registration[user]["password"]:
                return True
            else:
                return False

def login():
    username = input("Enter Username:")
    if check_username(username):
        password = input("Enter Password:")
        if check_password(username, password):
            print("Login Successful")
        else:
            print("Login Failed")
    else:
        print ("user does not exist")
login()




