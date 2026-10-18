
from flask import Flask
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

from models import db, User


app = Flask(__name__)

app.config["SECRET_KEY"] = "carrot"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///emp.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "student_login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

import sys
sys.modules["app"] = sys.modules["__main__"]

# Import controllers after initializing the app
import controllers


# Create database tables and default Admin
with app.app_context():
    db.create_all()

    admin_email = "admin@emp.local"

    admin = User.query.filter_by(email=admin_email).first()

    if admin is None:
        admin = User(
            name="Admin",
            email=admin_email,
            password=generate_password_hash("admin@123"),
            role="Admin",
            is_approved=True,
            is_active=True
        )

        db.session.add(admin)
        db.session.commit()


if __name__ == "__main__":
    app.run(debug=True, port=5000)






















































# def create_app():
#     app = Flask(__name__)
#     app.config['SECRET_KEY'] = 'carrot'
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://emp.db'

#     db.init_app(app)

#     login_manager = LoginManager()
#     login_manager.login_view = 'login'
#     login_manager.init_app(app)




#     @login_manager.user_loader

#     def load_user(user_id):
#         return User.query.get(int(user_id))

#     with app.app_context():
#         db.create_all()

#         if not  User.quer.filter_by(role='Admin').first():
#             admin = User(name='Admin',
#                             email ='admin@emp.com',
#                             password='admin123',
#                             role='admin',
#                             is_approved=True)
#             db.session.add(admin)
#             db.session.commit()
#     return app
# # @app.route("/")

# # def home() :
# #     return render_template("index.html")

# # @app.route("/login")

# # def login():
# #     return render_template('login.html')

# # @app.route("/signup")
# # def signup() :
# #     return render_template('signup.html')

# app = create_app()
# from controllers import *

# if __name__ == '__main__' :
#     app.run(debug = True)






