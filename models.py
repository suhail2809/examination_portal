from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(30), nullable=False)

    contact = db.Column(db.String(20))

    # # Student details
    # roll_number = db.Column(db.String(100), unique=True)
    # batch = db.Column(db.String(30))

    # # Examiner details
    # department = db.Column(db.String(100))
    # qualification = db.Column(db.String(100))

    # Account approval and activation
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime,default=datetime.utcnow,nullable=False)

    def get_id(self):
        return str(self.user_id)


# --------------------------------------------------
# 2. COURSE
# --------------------------------------------------

class Course(db.Model):
    __tablename__ = "courses"

    course_id = db.Column(db.Integer, primary_key=True)

    course_code = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    course_name = db.Column(db.String(100), nullable=False)
    descriptions = db.Column(db.Text)

    status = db.Column(
        db.String(20),
        default="Active",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )


# --------------------------------------------------
# 3. EXAMINATION
# --------------------------------------------------

class Examination(db.Model):
    __tablename__ = "examinations"

    exam_id = db.Column(db.Integer, primary_key=True)

    course_id = db.Column(
        db.Integer,
        db.ForeignKey("courses.course_id"),
        nullable=False
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    exam_type = db.Column(
        db.String(30),
        default="Viva",
        nullable=False
    )

    duration = db.Column(db.Integer, nullable=False)

    # Examination period
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    # Slot creation period
    slot_creation_start = db.Column(db.DateTime)
    slot_creation_end = db.Column(db.DateTime)

    # Student booking period
    booking_start = db.Column(db.DateTime)
    booking_end = db.Column(db.DateTime)

    max_marks = db.Column(
        db.Integer,
        default=100,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="Draft",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    course = db.relationship(
        "Course",
        backref=db.backref("examinations", lazy=True)
    )

    creator = db.relationship(
        "User",
        backref=db.backref("examinations_created", lazy=True),
        foreign_keys=[created_by]
    )


# --------------------------------------------------
# 4. RUBRIC
# --------------------------------------------------

class Rubric(db.Model):
    __tablename__ = "rubrics"

    rubric_id = db.Column(db.Integer, primary_key=True)

    examination_id = db.Column(
        db.Integer,
        db.ForeignKey("examinations.exam_id"),
        nullable=False
    )

    criteria_name = db.Column(db.String(100), nullable=False)
    max_marks = db.Column(db.Integer, nullable=False)

    weightage = db.Column(
        db.Float,
        default=0,
        nullable=False
    )

    description = db.Column(db.Text)

    examination = db.relationship(
        "Examination",
        backref=db.backref("rubrics", lazy=True)
    )


# --------------------------------------------------
# 5. EXAM SLOT
# --------------------------------------------------

class ExamSlot(db.Model):
    __tablename__ = "exam_slots"

    slot_id = db.Column(db.Integer, primary_key=True)

    examination_id = db.Column(
        db.Integer,
        db.ForeignKey("examinations.exam_id"),
        nullable=False
    )

    examiner_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    capacity = db.Column(db.Integer, nullable=False)

    status = db.Column(
        db.String(20),
        default="Available",
        nullable=False
    )

    examination = db.relationship(
        "Examination",
        backref=db.backref("exam_slots", lazy=True)
    )

    examiner = db.relationship(
        "User",
        backref=db.backref("exam_slots", lazy=True),
        foreign_keys=[examiner_id]
    )

    @property
    def booked_count(self):
        return sum(
            1 for booking in self.bookings
            if booking.status in ("Booked", "Completed")
        )

    @property
    def available_seats(self):
        return max(0, self.capacity - self.booked_count)


# --------------------------------------------------
# 6. BOOKING
# --------------------------------------------------

class Booking(db.Model):
    __tablename__ = "bookings"

    __table_args__ = (
        db.UniqueConstraint(
            "student_id",
            "examination_id",
            name="unique_student_examination"
        ),
    )

    booking_id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    examination_id = db.Column(
        db.Integer,
        db.ForeignKey("examinations.exam_id"),
        nullable=False
    )

    slot_id = db.Column(
        db.Integer,
        db.ForeignKey("exam_slots.slot_id"),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="Booked",
        nullable=False
    )

    booked_timing = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    cancelled_at = db.Column(db.DateTime)

    student = db.relationship(
        "User",
        backref=db.backref("bookings", lazy=True),
        foreign_keys=[student_id]
    )

    examination = db.relationship(
        "Examination",
        backref=db.backref("bookings", lazy=True)
    )

    slot = db.relationship(
        "ExamSlot",
        backref=db.backref("bookings", lazy=True)
    )


# --------------------------------------------------
# 7. EVALUATION
# --------------------------------------------------

class Evaluation(db.Model):
    __tablename__ = "evaluations"

    evaluation_id = db.Column(db.Integer, primary_key=True)

    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("bookings.booking_id"),
        unique=True,
        nullable=False
    )

    examiner_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    marks = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    remarks = db.Column(db.Text)

    is_published = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    published_at = db.Column(db.DateTime)

    examiner = db.relationship(
        "User",
        backref=db.backref("evaluations", lazy=True),
        foreign_keys=[examiner_id]
    )

    booking = db.relationship(
        "Booking",
        backref=db.backref("evaluation", uselist=False)
    )


# --------------------------------------------------
# 8. RUBRIC SCORE
# --------------------------------------------------

class RubricScore(db.Model):
    __tablename__ = "rubric_scores"

    __table_args__ = (
        db.UniqueConstraint(
            "evaluation_id",
            "rubric_id",
            name="unique_evaluation_rubric"
        ),
    )

    score_id = db.Column(db.Integer, primary_key=True)

    evaluation_id = db.Column(
        db.Integer,
        db.ForeignKey("evaluations.evaluation_id"),
        nullable=False
    )

    rubric_id = db.Column(
        db.Integer,
        db.ForeignKey("rubrics.rubric_id"),
        nullable=False
    )

    marks = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    evaluation = db.relationship(
        "Evaluation",
        backref=db.backref("scores", lazy=True)
    )

    rubric = db.relationship(
        "Rubric",
        backref=db.backref("scores", lazy=True)
    )

class ExaminationAssignment(db.Model):
    __tablename__ = "examination_assignments"

    __table_args__ = (
        db.UniqueConstraint(
            "examination_id",
            "examiner_id",
            name = "unique_examination_examiner"
        ),
    )

    assignment_id = db.Column(db.Integer, primary_key=True)
    examination_id = db.Column(db.Integer , db.ForeignKey("examinations.exam_id"),nullable=False)
    examiner_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    assigned_time= db.Column(db.DateTime, default= datetime.utcnow, nullable=False)

    examination= db.relationship("Examination", backref=db.backref("examiner_assignments"))
    examiner = db.relationship("User", backref=db.backref("examination_assignments"))






































# from flask_sqlalchemy import SQLAlchemy
# from flask_login import UserMixin
# from datetime import datetime


# db = SQLAlchemy()  #--> initialize yahan se hoga humlog ki database


# # pehle users bana rha hoon isi me admin,examiner
# # matlab hutiye proctor aur bs wale nalle login krenge
# class User(UserMixin, db.Model):
#     __tablename__ = "users"

#     user_id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False)

#     email = db.Column(db.String(120), nullable=False, unique=True)
#     password = db.Column(db.String(255), nullable=False)

#     role = db.Column(db.String(30), nullable=False)
#     # yahi role selection hoga

#     # is_active = db.Column(db.Boolean, default=True, nullable=False)

#     # created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

#     # -----------------------------------------------------------------------------------------------------------
#     # # student = db.relationship("Student", backref="user",lazy=True)
#     # # #one to one relation
#     # # examiner= db.relationship("Examiner", backref = "user", lazy= True )
#     # # #one to one relation
#     # exams_created = db.relationship("Examinations", backref="creator ", foreign_keys="Examination.created_by")

#     contact = db.Column(db.String(20))
#     roll_number = db.Column(db.String(100))  # if role is student
#     batch = db.Column(db.String(30))  # if role is student
#     department = db.Column(db.String(100))  # examiner
#     qualification = db.Column(db.String(100))  # examiner

#     ##admin ka approval
#     is_approved = db.Column(db.Boolean, default=False, nullable=False)
#     is_active = db.Column(db.Boolean, default=True, nullable=False)
#     created_at = db.Column(
#         db.DateTime,
#         default=datetime.utcnow,
#         nullable=False
#     )

#     def get_id(self):
#         return str(self.user_id)


# ##################################################################################
# ## class Student(db.Model):
# #     __tablename__= "students"


# #     student_id = db.Column(db.Integer,primary_key= True)

# #     user_id = db.Column(db.ForeignKey("users.user_id"),
# #                         unique= True, nullable=False)

# #     roll_number = db.Column(db.Integer, unique= True, nullable=False)

# #     batch = db.Column(db.String(50), nullable=False)


# #     user = db.relationship("User", backref= db.backref("student"))




# # class Examiner(db.Model):
# #     __tablename__ = "examiners"

# #     examiner_id = db.Column(db.Integer, primary_key = True)

# #     # connection of examiner and user table
# #     user_id = db.Column(db.ForeignKey("users.user_id"),
# #                         unique= True , nullable=False)

# #     department = db.Column(db.String(100), nullable=False)

# #     qualification= db.Column(db.String(150))


# #     ## admin approval to create examiner
# #     is_approved= db.Column(db.Boolean, default=False,nullable=False)

# #     #DEACTIVATE EXaminer
# #     is_active = db.Column(db.Boolean, default=True, nullable=False)


# #     # relation
# #     user= db.relationship("User",
# #                             backref = db.backref("examiner"))


# # -----------------------------------------------------------------------------------------------------------


# class Course(db.Model):
#     __tablename__ = "courses"

#     course_id = db.Column(db.Integer, primary_key=True)
#     course_code = db.Column(db.String(50), unique=True, nullable=False)

#     course_name = db.Column(db.String(100), nullable=False)
#     descriptions = db.Column(db.Text)

#     status = db.Column(db.String(20), default="Active", nullable=False)
#     created_at = db.Column(
#         db.DateTime,
#         default=datetime.utcnow,
#         nullable=False
#     )


# # -----------------------------------------------------------------------------------------------------------


# class Examination(db.Model):
#     __tablename__ = "examinations"

#     exam_id = db.Column(db.Integer, primary_key=True)
#     course_id = db.Column(
#         db.Integer,
#         db.ForeignKey("courses.course_id"),
#         nullable=False
#     )

#     created_by = db.Column(
#         db.Integer,
#         db.ForeignKey("users.user_id"),
#         nullable=False
#     )

#     title = db.Column(db.String(100), nullable=False)
#     description = db.Column(db.Text)

#     exam_type = db.Column(db.String(30), default="Viva", nullable=False)

#     duration = db.Column(db.Integer, nullable=False)

#     slot_creation_start = db.Column(db.DateTime)
#     slot_creation_end = db.Column(db.DateTime)

#     booking_start = db.Column(db.DateTime)
#     booking_end = db.Column(db.DateTime)

#     exam_date = db.Column(db.Date)
#     max_marks = db.Column(db.Integer, default=100, nullable=False)

#     status = db.Column(db.String(30), default="Draft", nullable=False)

#     created_at = db.Column(
#         db.DateTime,
#         default=datetime.utcnow,
#         nullable=False
#     )

#     course = db.relationship(
#         "Course",
#         backref=db.backref("examinations", lazy=True)
#     )

#     ##admin banayega course isliye reference to user table
#     creator = db.relationship(
#         "User",
#         backref=db.backref("examinations_created", lazy=True),
#         foreign_keys=[created_by]
#     )


# # -----------------------------------------------------------------------------------------------------------


# class Rubric(db.Model):
#     __tablename__ = "rubrics"

#     rubric_id = db.Column(db.Integer, primary_key=True)

#     examination_id = db.Column(
#         db.Integer,
#         db.ForeignKey("examinations.exam_id"),
#         nullable=False
#     )

#     criteria_name = db.Column(db.String(100), nullable=False)
#     max_marks = db.Column(db.Integer, nullable=False)
#     weightage = db.Column(db.Float, default=0, nullable=False)
#     description = db.Column(db.Text)

#     examination = db.relationship(
#         "Examination",
#         backref=db.backref("rubrics", lazy=True)
#     )


# # -----------------------------------------------------------------------------------------------------------


# class ExamSlot(db.Model):
#     __tablename__ = "exam_slots"

#     slot_id = db.Column(db.Integer, primary_key=True)

#     ##to connect examination table take foreign key examination_id
#     examination_id = db.Column(
#         db.Integer,
#         db.ForeignKey("examinations.exam_id"),
#         nullable=False
#     )

#     ## examiner course banayega jo examiner ka id lega user table se
#     examiner_id = db.Column(
#         db.Integer,
#         db.ForeignKey("users.user_id"),
#         nullable=False
#     )

#     date = db.Column(db.Date, nullable=False)
#     start_time = db.Column(db.Time, nullable=False)
#     end_time = db.Column(db.Time, nullable=False)

#     capacity = db.Column(db.Integer, nullable=False)

#     status = db.Column(
#         db.String(20),
#         default="Available",
#         nullable=False
#     )

#     examination = db.relationship(
#         "Examination",
#         backref=db.backref("exam_slots", lazy=True)
#     )

#     examiner = db.relationship(
#         "User",
#         backref=db.backref("exam_slots", lazy=True),
#         foreign_keys=[examiner_id]
#     )

#     @property
#     def booked_count(self):
#         return sum(
#             1 for booking in self.bookings
#             if booking.status in ("Booked", "Completed")
#         )

#     @property
#     def available_seats(self):
#         return max(0, self.capacity - self.booked_count)


# # -----------------------------------------------------------------------------------------------------------


# class Booking(db.Model):
#     __tablename__ = "bookings"

#     booking_id = db.Column(db.Integer, primary_key=True)

#     # book kya hoga examination aur karega kon students
#     # to foreign key se connect karenge

#     student_id = db.Column(
#         db.Integer,
#         db.ForeignKey("users.user_id"),
#         nullable=False
#     )

#     examination_id = db.Column(
#         db.Integer,
#         db.ForeignKey("examinations.exam_id"),
#         nullable=False
#     )

#     slot_id = db.Column(
#         db.Integer,
#         db.ForeignKey("exam_slots.slot_id"),
#         nullable=False
#     )

#     status = db.Column(db.String(20), default="Booked", nullable=False)

#     booked_timing = db.Column(
#         db.DateTime,
#         default=datetime.utcnow,
#         nullable=False
#     )

#     cancelled_at = db.Column(db.DateTime)

#     student = db.relationship(
#         "User",
#         backref=db.backref("bookings", lazy=True),
#         foreign_keys=[student_id]
#     )

#     examination = db.relationship(
#         "Examination",
#         backref=db.backref("bookings", lazy=True)
#     )

#     slot = db.relationship(
#         "ExamSlot",
#         backref=db.backref("bookings", lazy=True)
#     )


# # -----------------------------------------------------------------------------------------------------------


# class Evaluation(db.Model):
#     __tablename__ = "evaluations"

#     evaluation_id = db.Column(db.Integer, primary_key=True)

#     booking_id = db.Column(
#         db.Integer,
#         db.ForeignKey("bookings.booking_id"),
#         unique=True,
#         nullable=False
#     )

#     examiner_id = db.Column(
#         db.Integer,
#         db.ForeignKey("users.user_id"),
#         nullable=False
#     )

#     marks = db.Column(db.Integer, default=0, nullable=False)
#     remarks = db.Column(db.Text)

#     is_published = db.Column(db.Boolean, default=False, nullable=False)
#     published_at = db.Column(db.DateTime)

#     examiner = db.relationship(
#         "User",
#         backref=db.backref("evaluations", lazy=True),
#         foreign_keys=[examiner_id]
#     )

#     booking = db.relationship(
#         "Booking",
#         backref=db.backref("evaluation", uselist=False)
#     )


# # -----------------------------------------------------------------------------------------------------------


# class RubricScore(db.Model):
#     __tablename__ = "rubric_scores"

#     score_id = db.Column(db.Integer, primary_key=True)

#     evaluation_id = db.Column(
#         db.Integer,
#         db.ForeignKey("evaluations.evaluation_id"),
#         nullable=False
#     )

#     rubric_id = db.Column(
#         db.Integer,
#         db.ForeignKey("rubrics.rubric_id"),
#         nullable=False
#     )

#     marks = db.Column(db.Integer, default=0, nullable=False)

#     evaluation = db.relationship(
#         "Evaluation",
#         backref=db.backref("scores", lazy=True)
#     )

#     rubric = db.relationship(
#         "Rubric",
#         backref=db.backref("scores", lazy=True)
#     )
