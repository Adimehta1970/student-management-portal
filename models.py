from run import db
from flask_login import UserMixin

enrollments = db.Table('enrollments',
    db.Column('student_id', db.Integer, db.ForeignKey('students.student_id')),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.course_id'))
)

student_professor = db.Table('student_professor',
    db.Column('student_id', db.Integer, db.ForeignKey('students.student_id')),
    db.Column('professor_id', db.Integer, db.ForeignKey('professors.professor_id'))
)   

class Student(db.Model, UserMixin):
    __tablename__ = 'students'

    student_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
    courses = db.relationship('Course', secondary=enrollments, backref='students')
    professors = db.relationship('Professor', secondary=student_professor, backref='students')

    def __repr__(self):
        return f'Person with name: {self.name}'
    
    def get_id(self):
           return (self.student_id)

class Professor(db.Model, UserMixin):
    __tablename__ = 'professors'

    professor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'))   

    def __repr__(self):
        return f'Person with name: {self.name}'
    
    def get_id(self):
           return (self.professor_id)

class Course(db.Model):
    __tablename__ = 'courses'
    course_id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.Text)

class Attendance(db.Model):
    __tablename__ = 'attendance'
    attendance_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'))
    count = db.Column(db.Integer, nullable=False)  

class Grade(db.Model):
    __tablename__ = 'grades'
    grade_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'))
    grade = db.Column(db.Text)