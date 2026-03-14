from premium_users import PremiumUser
from users_password import Password
from utils import get_quote

def main():
    print ( get_quote() )
    pr_obj = PremiumUser("pr", "Welcome PR")
    ar_obj = PremiumUser("ar", "Welcome AR")
    rj_obj = PremiumUser("rj", "Welcome RJ")
    if pr_obj.user_validation():
        print (f"username: {pr_obj.username} found")
    if ar_obj.user_validation():
        print(f"username: {ar_obj.username} found")
    if rj_obj.user_validation():
        print(f"username: {rj_obj.username} found")

    pr_pass_obj = Password("pr")
    ar_pass_obj = Password("ar")
    rj_pass_obj = Password("rj")

    pr_pass_obj.password_validation()
    ar_pass_obj.password_validation()
    rj_pass_obj.password_validation()

if __name__ == "__main__":
    main()

