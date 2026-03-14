# Login App
# Functionality
# 1. Check if the user name is found
# 2. Check if the password is correct
# 3. Max password attempts are 3

#Registration Data
registration = {
    'user1': {"login_name": "pr", "password": "pr123"},
    'user2': {'login_name': "rj", "password": "rj123"},
    'user3': {'login_name': "rav", "password": "rav123"},
}
#print (registration['user1']['login_name'])

# Login Functionality
username = input("Enter Username:")
#print (username)

for user in registration:
    if username == registration[user]["login_name"]:
        print (f"Username: {username} exists")
        password = input("Enter Password:")
        # Check the password
        if password == registration[user]["password"]:
            print (f"Password is correct! Access granted")
        else:
            print (f"Password is incorrect! Access denied")









