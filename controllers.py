from flask import render_template, request, redirect, url_for, abort, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Course, Examination, Rubric, ExamSlot,Booking, RubricScore , Evaluation, ExaminationAssignment
from app import app
from datetime import date, datetime, time

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
        department=request.form["department"]
        contact= request.form["contact"]

        existing_user= User.query.filter_by(email=email).first()

        if existing_user:
            return redirect(url_for("examiner_login"))
        
        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            department=department,
            contact=contact,
            role="Examiner",
            is_approved= False,
            is_active=True)

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

    assignments = ExaminationAssignment.query.filter_by(examiner_id =current_user.user_id).all()

    return render_template("examiner_dashboard.html", assignments=assignments)


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


@app.route("/admin/examiner-approvals")
@login_required

def examiner_approvals():
    if current_user.role!= "Admin":
        abort(403)

    examiner_approval = User.query.filter_by(role="Examiner", is_approved=False, is_active=True).all()

    return render_template("examiner_approval.html",examiner_approval=examiner_approval)


@app.route("/admin/manage-examiners")
@login_required

def manage_examiners():
    if current_user.role!="Admin":
        abort(403)

    search =  request.args.get("search", "").strip()  ### ye search  wala name isme input feild html ka name hai

    examiners = User.query.filter(User.role=="Examiner", User.name.ilike(f"%{search}%")).order_by(User.user_id.desc()).all()

    return render_template("manage_examiners.html", examiners=examiners, search=search)

@app.route("/admin/manage-examiner/<int:user_id>/status", methods=["POST"])
@login_required

def examiner_status(user_id):
    if current_user.role !="Admin":
        abort(403)

    examiner= User.query.filter_by(user_id=user_id, role="Examiner").first_or_404()

    examiner.is_approved = True
    examiner.is_active = not examiner.is_active
    db.session.commit()

    return redirect(url_for("manage_examiners"))


@app.route("/admin/examiners/<int:user_id>/delete", methods=["POST"])
@login_required

def delete_examiner(user_id):
    if current_user.role!= "Admin":
        abort(403)

    examiner = User.query.filter_by(user_id=user_id, role="Examiner").first_or_404()

    db.session.delete(examiner)
    db.session.commit()

    return redirect(url_for("manage_examiners"))

### logout route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


#### assigning examiner date- 25 oct 

@app.route("/admin/assign-examiners", methods=["GET","POST"])
@login_required

def assign_examiners():
    if current_user.role!="Admin":
        abort(403)

    error =None

    if request.method=="POST":
        examination_id = request.form.get("examination_id","")
        examiner_id = request.form.get("examiner_id","")

        if not examination_id.isdigit() or not examiner_id.isdigit():
            error = "Please select valid examiner"
        else:
            examination = Examination.query.get(int(examination_id))

            examiner = User.query.filter_by(user_id= int(examiner_id), role="Examiner", is_approved=True,
                                            is_active=True).first()

            if not examiner or not examination:
                error = "wrong examination and examiner"
            else:
                existing = ExaminationAssignment.query.filter_by(examination_id = examination.exam_id,examiner_id= examiner.user_id).first()

                if existing:
                    error = "examiner already assigned"

                else:
                    assignment = ExaminationAssignment(examination_id=examination.exam_id, examiner_id= examiner.user_id)

                    db.session.add(assignment)
                    db.session.commit()

                    return redirect(url_for("assign_examiners"))


    examinations = Examination.query.order_by(Examination.exam_id.desc()).all()

    examiners = User.query.filter_by(role="Examiner", is_approved=True, is_active =True).order_by(User.name).all()

    assignments = ExaminationAssignment.query.order_by(ExaminationAssignment.assignment_id.desc()).all()

    return render_template("assign_examiners.html", examinations=examinations, examiners=examiners,assignments=assignments, error=error)


### edit assignments 25 oct
@app.route("/admin/assignments/edit_assignment/<int:assignment_id>", methods=["GET","POST"])
@login_required

def edit_assignment(assignment_id):
    if current_user.role!= "Admin":
        abort(403)

    assignment = ExaminationAssignment.query.get_or_404(assignment_id)

    if request.method== "POST":   #### ye check krega form html template jo post se tha wo submit hua ki nhi
        
        examiner_id = request.form.get("examiner_id", "")

        examiner = User.query.filter_by(user_id =int(examiner_id), role="Examiner",
                                        is_approved=True, is_active=True).first()

        existing = ExaminationAssignment.query.filter_by(examination_id = assignment.examination_id, examiner_id = examiner.user_id).first()

        if existing and existing.assignment_id != assignment.assignment_id:
            abort(400)
        assignment.examiner_id = examiner.user_id
        db.session.commit()

        return redirect(url_for("assign_examiners"))

    examiners = User.query.filter_by(role="Examiner", is_approved=True, is_active=True).all()


    return render_template("edit_assignment.html", assignment=assignment,examiners=examiners)

#### delete assignments 
@app.route("/admin/assignments/delete_assignment/<int:assignment_id>", methods=["POST"])
@login_required
def delete_assignment(assignment_id):
    if current_user.role != "Admin":
        abort(403)

    assignment = ExaminationAssignment.query.get_or_404(assignment_id)

    db.session.delete(assignment)
    db.session.commit()

    return redirect(url_for("assign_examiners"))



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

        if not existing_course:
            
            course = Course(
                course_code = course_code, course_name= course_name, descriptions=descriptions, status="Active")
            
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

    return redirect(url_for("manage_courses"))

@app.route("/admin/courses/edit_courses/<int:course_id>", methods=["GET","POST"])
@login_required

def edit_course(course_id):
    if current_user.role!= "Admin":
        abort(403)

    course = Course.query.get_or_404(course_id)

    if request.method== "POST":
        course.course_code = request.form.get("course_code")
        course.course_name = request.form.get("course_name")
        course.descriptions = request.form.get("descriptions")

        db.session.commit()

        return redirect(url_for("manage_courses"))

    return render_template("edit_courses.html", course=course)


@app.route("/admin/manage-examinations", methods=["GET","POST"])
@login_required

def manage_exams():
    if current_user.role!="Admin":
        abort(403)
    
    if request.method=="POST":

        course_id = int(request.form.get("course_id"))
        title = request.form.get("title")
        description = request.form.get("description")
        exam_type = request.form.get("exam_type")
        duration = int(request.form.get("duration"))
        start_date = date.strptime(request.form.get("start_date"), "%Y-%m-%d") if request.form.get("start_date") else None

        end_date = date.strptime(request.form.get("end_date"), "%Y-%m-%d") if request.form.get("end_date") else None
        slot_creation_start = datetime.strptime(request.form.get("slot_creation_start"), "%Y-%m-%dT%H:%M") if request.form.get("slot_creation_start") else None

        slot_creation_end = datetime.strptime(
            request.form.get("slot_creation_end"), "%Y-%m-%dT%H:%M"
        ) if request.form.get("slot_creation_end") else None

        booking_start = datetime.strptime(
            request.form.get("booking_start"), "%Y-%m-%dT%H:%M"
        ) if request.form.get("booking_start") else None

        booking_end = datetime.strptime(
            request.form.get("booking_end"), "%Y-%m-%dT%H:%M"
        ) if request.form.get("booking_end") else None
        max_marks = int(request.form.get("max_marks"))
    


        exam  = Examination(
            course_id = course_id,
            created_by = current_user.user_id, title = title , description = description , 
            exam_type = exam_type , duration = duration, start_date=start_date, end_date=end_date,
            slot_creation_start = slot_creation_start, slot_creation_end = slot_creation_end , 
            booking_start= booking_start, booking_end= booking_end, max_marks= max_marks)

        db.session.add(exam)
        db.session.commit()
        print("Examination saved:", exam.title)

        return redirect(url_for("manage_exams"))

    
    courses = Course.query.all()

    search = request.args.get("search", "").strip()

    examinations = Examination.query

    if search:
        examinations = examinations.filter(
            Examination.title.ilike(f"%{search}%")
        )

        if search.isdigit():
            examinations = Examination.query.filter(
                db.or_(
                    Examination.title.ilike(f"%{search}%"),
                    Examination.exam_id == int(search)
                )
            )

    examinations = examinations.order_by(
        Examination.exam_id.desc()
    ).all()

    return render_template(
        "manage_examinations.html",
        courses=courses,
        examinations=examinations
    )

@app.route("/admin/examinations/exam-status/<int:exam_id>", methods=["POST"])
@login_required

def exam_status(exam_id):
    if current_user.role!="Admin":
        abort(403)

    exam = Examination.query.get_or_404(exam_id)

    if exam.status == "Active":
        exam.status = "Inactive"
    else:
        exam.status = "Active"

    db.session.commit()

    return redirect(url_for("manage_exams"))


@app.route("/admin/examinations/edit-exams/<int:exam_id>", methods=["GET","POST"])
@login_required

def edit_exam(exam_id):
    if current_user.role!= "Admin":
        abort(403)

    exam = Examination.query.get_or_404(exam_id)

    if request.method== "POST":
        exam.title = request.form.get("title")
        exam.description = request.form.get("description")
        exam.exam_type = request.form.get("exam_type")
        exam.duration = request.form.get("duration")
        exam.max_marks = request.form.get("max_marks")

        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        exam.start_date = (date.strptime(start_date, "%Y-%m-%d")
                            if start_date else None)
        exam.end_date = (
            date.strptime(end_date, "%Y-%m-%d")
            if end_date else None)
        

        slot_creation_start = request.form.get("slot_creation_start")
        slot_creation_end = request.form.get("slot_creation_end")
        booking_start = request.form.get("booking_start")
        booking_end = request.form.get("booking_end")

        exam.slot_creation_start = (
            datetime.strptime(slot_creation_start, "%Y-%m-%dT%H:%M")
            if slot_creation_start else None
        )

        exam.slot_creation_end = (
            datetime.strptime(slot_creation_end, "%Y-%m-%dT%H:%M")
            if slot_creation_end else None
        )

        exam.booking_start = (
            datetime.strptime(booking_start, "%Y-%m-%dT%H:%M")
            if booking_start else None
        )

        exam.booking_end = (
            datetime.strptime(booking_end, "%Y-%m-%dT%H:%M")
            if booking_end else None
        )
        db.session.commit()

        return redirect(url_for("manage_exams"))

    return render_template("edit_exams.html", exam=exam )  ## left wala exam means we have choosen this exam variable to use in our template edit_exams.html
                                                            ## and right wala exam ye hai python varibale jo is route me define kiya hu hai exactly me dono same hi hai

@app.route("/admin/examinations/delete/<int:exam_id>", methods=["POST"])
@login_required
def delete_exams(exam_id):
    if current_user.role != "Admin":
        abort(403)

    exam = Examination.query.get_or_404(exam_id)

    db.session.delete(exam)
    db.session.commit()
    
    return redirect(url_for("manage_exams"))



@app.route("/examiner/create-slots/<int:exam_id>", methods=["GET","POST"])
@login_required
def create_slots(exam_id):
    if current_user.role!= "Examiner":
        abort(403)
    if not current_user.is_active or not current_user.is_approved:
        logout_user()
        return redirect(url_for("examiner_login"))

    assignment = ExaminationAssignment.query.filter_by(examination_id=exam_id, examiner_id=current_user.user_id).first()

    if not assignment:
        abort(403)
    examination= Examination.query.get_or_404(exam_id)

    if request.method=='POST':
        slot_date= date.fromisoformat(request.form.get("date"))
        start_time= time.fromisoformat(request.form.get("start_time"))
        end_time = time.fromisoformat(request.form.get("end_time"))
        capacity = int(request.form.get("capacity"))

        if start_time >= end_time or capacity <=0:
            abort(400, description="a")
        if not examination.start_date or not examination.end_date:
            abort(400, description="b")
        
        if not (examination.start_date <= slot_date <=examination.end_date):
            abort(400, description="c")
        now= datetime.now()

        if not examination.slot_creation_start or not examination.slot_creation_end:
            abort(400, description="d")

        if not (examination.slot_creation_start  <= examination.slot_creation_end):
            abort(400, description="e")

        slot = ExamSlot(
            examination_id = exam_id,
            examiner_id = current_user.user_id,
            date= slot_date,
            start_time =start_time,
            end_time= end_time,
            capacity= capacity
        )
        db.session.add(slot)
        db.session.commit()

        return redirect(url_for("examiner_dashboard"))

    return render_template("create_slots.html" ,  examination=examination)

### view slots by admin

@app.route("/admin/manage-slots")
@login_required

def manage_slots():
    if current_user.role!="Admin":
        abort(403)

    slots = ExamSlot.query.order_by(ExamSlot.date, ExamSlot.start_time).all()

    return render_template("manage_slots.html", slots=slots)

### edit and cancel examslots by admin

@app.route("/admin/edit-slots/<int:slot_id>", methods=["GET","POST"])
@login_required

def edit_slots(slot_id):
    if current_user.role!="Admin":
        abort(403)

    slot = ExamSlot.query.get_or_404(slot_id)
    if request.method=="POST":
        slot.date= date.fromisoformat(request.form.get('date'))
        slot.start_time= time.fromisoformat(request.form.get('start_time'))
        slot.end_time = time.fromisoformat(request.form.get('end_time'))
        slot.capacity = int(request.form.get('capacity'))

        if not slot.start_time <= slot.end_time:
            abort(400, description="start time must be before end time; fix your time slot")

        if  slot.capacity < 1:
            abort(400, description="capacity cant be empty or zero")

        if slot.capacity < slot.booked_count:
            abort(400, description="capacity cant be lesser than existing bookings")

        db.session.commit()
        return redirect(url_for("manage_slots"))
            
    return render_template("edit_slots.html", slot=slot)


@app.route("/admin/cancel-slots/<int:slot_id>", methods=["POST"])
@login_required
def cancel_slots(slot_id):

    if current_user.role!="Admin":
        abort(403)
    slot = ExamSlot.query.get_or_404(slot_id)

    if slot.booked_count >=1:
        abort(403, description="cant be cancelled, booking present")

    
    slot.status = "cancelled"

    db.session.commit()
    return redirect(url_for('manage_slots'))
    



