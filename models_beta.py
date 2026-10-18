# from flask_sqlalchemy import SQLAlchemy
# from flask_login import UserMixin
# from datetime import datetime 


# db = SQLAlchemy()  #--> initialize yahan se hoga humlog ki databsse


# # pehle users bana rha hoon isi me admin,examiner
# # matlab hutiye proctor  aur bs wale nalle login krenge
# class User(UserMixin, db.Model):
#     __tablename__ = "users"

#     user_id = db.Column(db.Integer, primary_key = True)
#     name = db.Column(db.String(50), nullable= False)

#     email= db.Column(db.String(50), nullable=False, unique = True )
#     password= db.Column(db.String(255), nullable = False)

#     role  = db.Column(db.String(30),nullable=False)
#     # yahi role selection hoga 

# #     is_active = db.Column(db.Boolean, default=True, nullable=False)

# #     created_at = db.Column(db.DateTime, default= datetime.utcnow, nullable=False)

# # -----------------------------------------------------------------------------------------------------------

# #     # student = db.relationship("Student", backref="user",lazy=True)
# #     # #one to one relation
# #     # examiner= db.relationship("Examiner", backref = "user", lazy= True )
# #     # #one to one relation    
# #     exams_created = db.relationship("Examinations", backref="creator ", foreign_keys="Examination.created_by")

#     contact = db.Column(db.String(20))
#     roll_number = db.Column(db.String(100))  # if role is student
#     batch = db.Column(db.String(30)) # if role is student 
#     department= db.Column(db.String(100))        #examiner
#     qualification = db.Column(db.String(100))     # examiner


#     ##admin approval
#     is_approved = db.Column(db.Boolean, default=False)
#     is_active = db.Column(db.Boolean, default=True)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)


#     def get_id(self):
#         return str(self.user_id)
    

# ##################################################################################
# ## class Student(db.Model):
# #     __tablename__= "students"


# #     student_id = db.Column(db.Integer,primary_key= True)

# #     user_id = db.Column(db.Integer, db.Foreign_key("users.user_id"),
# #                         unique= True, nullable=False)

# #     roll_number = db.Column(db.Integer, unique= True, nullable=False)

# #     batch = db.Column(db.String(50), nullable=False)


# #     user = db.relationship("User", backref= db.backref("student"))




# # class Examiner(db.Model):
# #     __tablename__ = "examiners"

# #     examiner_id = db.Column(db.Integer, primary_key = True)

# #     # connection of examiner and user table
# #     user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"),
# #                         unique= True , nullable=False)

# #     department = db.Column(db.String(100), nullable=False)

# #     qualification= db.column(db.String(150))


# #     ## admin approval to create examiner 
# #     is_approved= db.Column(db.Boolean, default=False,nullable=False)

# #     #DEACTIVATE EXaminer 

# #     is_active = db.Column(db.Boolean, default=True, nullable=False)


# #     # relation

# #     user= db.relationship("User", 
# #                             backref = db.backref("examiner"))




# class Course(db.Model):
#     __tablename__ = "courses"

#     course_id = db.Column(db.Integer, primary_key = True)
#     course_code = db.Column(db.String(50), unique = True, nullable= False)

#     course_name = db.Column(db.String(100), nullable=False)
#     descriptions = db.Column(db.Text)

#     status = db.Column(db.String(20), default="Inactive",nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)





# class Enrollment(db.Model):
#     __tablename__ = "enrollments"

#     enrollment_id = db.Column(db.Integer, primary_key =True)
    
#     student_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
#     course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'), nullable=False)
#     enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)


#     student = db.relationship('User', backref='enrollments')

#     course  = db.relationship('Course', backref= 'enrollments')



# class Examination(db.Model):
#     __tablename__= 'examinations'

#     exam_id = db.Column(db.Integer, primary_key=True)
#     course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'), nullable=False)
    
#     created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)


#     title= db.Column(db.String(100), nullable=False)
#     description= db.Column(db.Text)

#     exam_type = db.Column(db.String(30), default='Vivas')

#     duration = db.Column(db.Integer)

#     slot_creation_start = db.Column(db.Date)
#     slot_creation_end = db.Column(db.Date)
#     booking_start = db.Column(db.Date)
#     booking_end = db.Column(db.Date)
#     exam_date = db.Column(db.Date)
#     max_marks = db.Column(db.Integer, default = 100)

#     status = db.Column(db.String(20), default = "Draft", nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)


#     course = db.relationship('Course', backref='examinations')
    
#     ##admin banayega course isliye refernce to user table 
#     creator = db.relationship('User', backref = 'examinations_created')


# class Rubric(db.Model):
#     __tablename__ = "rubrics"

#     rubric_id = db.Column(db.Integer, primary_key=True)
#     examination_id = db.Column(db.Integer, db.ForeignKey("examinations.exam_id"), nullable=False)

#     criteria_name = db.Column(db.String(100), nullable=False)
#     max_marks = db.Column(db.Integer, nullable=False)
#     weightage = db.Column(db.Float, default=0)
#     description = db.Column(db.Text)

#     examination = db.relationship("Examination", backref="rubrics")


# class ExamSlot(db.Model):
#     __tablename__ = 'exam_slots'

#     slot_id = db.Column(db.Integer, primary_key=True)

#     ##too connect examination table take foreign key examination_id
#     examination_id = db.Column(db.Integer, db.ForeignKey('examinations.exam_id'), nullable=False)
#     ## examiner course banayega jo examiner ka id lega user table se
#     examiner_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)


#     date = db.Column(db.Date, nullable=False)
    
#     start_time = db.Column(db.Time, nullable=False)
    
#     end_time = db.Column(db.Time, nullable=False)
    
#     capacity = db.Column(db.Integer, nullable=False)
#     status = db.Column(db.String(20), default='Available',nullable=False)

#     examination= db.relationship('Examination', backref='exam_slots')
#     examiner = db.relationship('User', backref = 'exam_slots')

#     @property
#     def booked_count(self):
#         return sum(1 for b in self.bookings if b.status in ("Booked", "Completed"))

#     @property
#     def available_seats(self):
#         return self.capacity - self.booked_count

# class Booking(db.Model):
#     __tablename__ = 'bookings'


#     booking_id = db.Column(db.Integer, primary_key =True)

#     ##book kya hoga examination aur karega kon students
#     #to foreign key se sonnect krrrr

#     student_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable= False, )

#     examination_id = db.Column(db.Integer, db.ForeignKey('examinations.exam_id'), nullable=False)

#     slot_id = db.Column(db.Integer, db.ForeignKey('exam_slots.slot_id'),nullable=False)


#     status  = db.Column(db.String(20), default= "booked")
#     booked_timing= db.Column(db.DateTime, default= datetime.utcnow)
    


#     student = db.relationship('User', backref='bookings')
#     examination= db.relationship('Examination', backref = 'bookings')

#     slot =  db.relationship('ExamSlot', backref= 'bookings')




# class Evaluation(db.Model):
#     __tablename__ = 'evaluations'

#     evaluation_id = db.Column(db.Integer, primary_key= True)

#     booking_id = db.Column(db.Integer, db.ForeignKey('bookings.booking_id'), unique=True, nullable=False)

#     examiner_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

#     marks= db.Column(db.Integer, default=0)
#     remarks = db.Column(db.Text)
#     is_result = db.Column(db.Boolean, default= False)
#     result_time=db.Column(db.DateTime, default =datetime.utcnow)

#     examiner = db.relationship('User', backref= 'evaluations')
#     booking  = db.relationship('Booking', backref= db.backref('evaluation', uselist=False))


# class RubricScore(db.Model):
#     __tablename__= "rubric_scores"

#     score_id = db.Column(db.Integer, primary_key=True )

#     evaluation_id= db.Column(db.Integer, db.ForeignKey("evaluations.evaluation_id"), nullable=False)

#     rubric_id= db.Column(db.Integer, db.ForeignKey("rubrics.rubric_id"), nullable=False)

#     marks= db.Column(db.Integer, default = 0)

#     evaluation = db.relationship("Evaluation", backref="scores")
#     rubric = db.relationship("Rubric")

