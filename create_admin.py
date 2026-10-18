# from app import app
# from models import db,User
# from werkzeug.security import generate_password_hash

# from getpass import getpass


# with app.app_context():

#     email= input("Enter admin email:").strip().lower()

#     user_exist= User.query.filter_by(email=email).first()

#     if user_exist:
#         print("admin exists")
#     else:

#         name= input