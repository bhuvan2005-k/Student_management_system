from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=True) 
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(10), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contact = db.Column(db.String(20), nullable=True)
    deleted = db.Column(db.Boolean, default=False)  # Soft delete flag

    attendance_records = db.relationship(
        'Attendance', backref='student', cascade='all, delete-orphan'
    )
    messages = db.relationship(
        'Message', backref='student', cascade='all, delete-orphan'
    )

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False)  # e.g., Present, Absent
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    sender = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)


