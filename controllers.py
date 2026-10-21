from flask import render_template, request, redirect, url_for, abort, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Course, Examination, Rubric, ExamSlot,Booking, RubricScore 
from app import app



def dashboard_redirect(user):
    if user.role=="Admin":
        return redirect(url_for("admin_dashboard"))

    elif user.role=="Examiner":
        return redirect(url_for("examiner_dashboard"))
    elif user.role=="Student":
        return redirect(url_for("student_dashboard"))

    abort(403)



###homepage####

@app.route("/")
def index():
    return render_template("index.html")


###### student signup #######

@app.route("/student/signup",  methods=["GET","POST"])
def student_signup():

    
    if request.method== "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        contact = request.form["contact"]

        existing_user= User.query.filter_by(email=email).first()

        if existing_user:
            return redirect(url_for("student_signup"))

        user= User(name=name,
                    email=email,
                    password=generate_password_hash(password),
                    contact=contact,
                    role='Student',
                    # is_approved=True,
                    is_active=True)

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("student_login"))

    return render_template("student_signup.html")

#####examiner ka signupp ---------####


@app.route("/examiner/signup", methods=["GET", "POST"])
def examiner_signup():
    if request.method=="POST":
        name = request.form["name"]
        email= request.form["email"]
        password=request.form["password"]
        contact= request.form["contact"]

        existing_user= User.query.filter_by(email=email).first()

        if existing_user:
            return redirect(url_for("examiner_login"))


        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            contact=contact,
            role="Examiner",
            is_approved= False,
            is_active=True

        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("examiner_login"))
    return render_template("examiner_signup.html")



#####student login

@app.route("/student/login", methods=["GET", "POST"])
def student_login():
    if request.method=="POST":

        email= request.form["email"]
        password= request.form["password"]

        user= User.query.filter_by(email=email, role="Student").first()


        if user and user.is_active and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("student_dashboard"))


    return render_template("student_login.html")



###  examiner login 


@app.route("/examiner/login", methods=["GET", "POST"])
def examiner_login():

    if request.method =="POST":

        email = request.form["email"]
        password= request.form["password"]

        user = User.query.filter_by(email=email, role="Examiner").first()

        if user and check_password_hash(user.password,password):
            if not user.is_active:
                flash ("your account is inactive")
            elif not user.is_approved:
                flash("your acc is waiting for admin approval")
            else:
                login_user(user)
                return redirect(url_for("examiner_dashboard"))


    return render_template("examiner_login.html")



#### admin login

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method=="POST":
        email = request.form["email"]
        password= request.form["password"]

        user = User.query.filter_by(email=email, role="Admin").first()

        if user and user.is_active and check_password_hash(user.password,password):
            login_user(user)

            return redirect(url_for("admin_dashboard"))


    return render_template("admin_login.html")


### student dashboard
@app.route("/student/dashboard")
@login_required
def student_dashboard():
    if current_user.role!="Student":
        abort(403)

    return render_template("student_dashboard.html")


#### examiner dasboard

@app.route("/examiner/dashboard")
@login_required
def examiner_dashboard():
    if current_user.role!="Examiner":
        abort(403)

    if not current_user.is_active or not current_user.is_approved:
        logout_user()
        return redirect(url_for("examiner_login"))

    return render_template("examiner_dashboard.html")


## admin dashboard

@app.route("/admin/dashboard")
@login_required  #####flask login decorator matlab user ko dashboard access karne se pehle login krega
def admin_dashboard():
    if current_user.role!="Admin":
        abort(403)

    examiner_approval = User.query.filter_by(role='Examiner', is_approved=False, is_active=True).all()


    total_students = User.query.filter_by(role="Student").count()
    total_examiners = User.query.filter_by(role="Examiner").count()
    total_courses = Course.query.count()

    total_examinations = Examination.query.count()
    total_examination_slots  = ExamSlot.query.count()
    total_bookings = Booking.query.count()



    return render_template("admin_dashboard.html", examiner_approval=examiner_approval,
                            total_students= total_students, total_examiners=total_examiners,total_courses = total_courses,
                                        total_examinations = total_examinations, total_examination_slots = total_examination_slots,
                                            total_bookings = total_bookings)
##                                            left side html template variable, right side waala python varb name jisme databases se list aya hai

@app.route("/admin/approve-examiner/<int:user_id>", methods=["POST"])
@login_required

def approve_examiner(user_id):
    if current_user.role !="Admin":
        abort(403)

    examiner= User.query.filter_by(user_id=user_id, role="Examiner").first_or_404()

    examiner.is_approved = True
    db.session.commit()


    return redirect(url_for("admin_dashboard"))




### logout route

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))



### course manage ###

@app.route("/admin/courses", methods=["GET","POST"])
@login_required

def manage_courses():
    if current_user.role!= "Admin":
        abort(403)

    if request.method == "POST":

        course_code = request.form.get("course_code")
        course_name = request.form.get("course_name")
        descriptions = request.form.get("descriptions")

        existing_course = Course.query.filter_by(course_code= course_code).first()

        if existing_course:
            flash("Course code already exists")
        else:
            course = Course(
                course_code = course_code, course_name= course_name, descriptions=descriptions, status="Active"
            )

            db.session.add(course)
            db.session.commit()

            return redirect(url_for("manage_courses"))


    courses = Course.query.order_by(Course.course_id.desc()).all()

    return render_template("manage_courses.html", courses= courses)




@app.route("/admin/courses/delete/<int:course_id>", methods=["POST"])
@login_required
def delete_course(course_id):
    if current_user.role != "Admin":
        abort(403)

    course = Course.query.get_or_404(course_id)

    db.session.delete(course)
    db.session.commit()

    flash("Course deleted successfully!")
    return redirect(url_for("manage_courses"))





@app.route("/admin/examiner-approvals")
@login_required

def examiner_approvals():
    if current_user.role!= "Admin":
        abort(403)

    examiner_approval = User.query.filter_by(role="Examiner", is_approved=False, is_active=True).all()

    return render_template("examiner_approval.html",examiner_approval=examiner_approval)