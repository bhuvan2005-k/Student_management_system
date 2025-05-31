from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Student, Attendance, Message
from datetime import datetime, date
from sqlalchemy import and_, or_ 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key_here'

db.init_app(app)

# Create tables once at first request
@app.before_request
def create_tables_once():
    if not hasattr(app, 'tables_created'):
        with app.app_context():
            db.create_all()
        app.tables_created = True

@app.route('/')
def index():
    # Show only non-deleted students
    students = Student.query.filter((Student.deleted == False) | (Student.deleted == None)).all()
    return render_template('index.html', students=students)


@app.route('/student/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        roll_no = request.form['roll_no']
        name = request.form['name']
        dob_str = request.form['dob']
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None
        age = int(request.form['age'])
        gender = request.form['gender']
        grade = request.form['grade']
        email = request.form['email']
        contact = request.form['contact']

        existing = Student.query.filter(
            (Student.email == email) | (Student.roll_no == roll_no)
        ).first()

        if existing:
            if existing.deleted:
                existing.roll_no = roll_no
                existing.name = name
                existing.dob = dob
                existing.age = age
                existing.gender = gender
                existing.grade = grade
                existing.email = email
                existing.contact = contact
                existing.deleted = False
                db.session.commit()
                flash('Previously deleted student restored and updated!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Student with this email or roll number already exists.', 'danger')
                return redirect(url_for('add_student'))

        student = Student(
            roll_no=roll_no,
            name=name,
            dob=dob,
            age=age,
            gender=gender,
            grade=grade,
            email=email,
            contact=contact,
        )
        db.session.add(student)
        db.session.commit()
        flash('Student added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('add_student.html')


@app.route('/student/<int:student_id>/update', methods=['GET', 'POST'])
def update_student(student_id):
    student = Student.query.get_or_404(student_id)
    if request.method == 'POST':
        student.roll_no = request.form['roll_no']
        student.name = request.form['name']
        # Convert dob from string to date, handle empty string gracefully
        dob_str = request.form.get('dob')
        if dob_str:
            try:
                student.dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format for DOB.', 'danger')
                return redirect(url_for('update_student', student_id=student_id))
        else:
            student.dob = None
        student.age = int(request.form['age'])
        student.gender = request.form.get('gender') or None
        student.grade = request.form['grade']
        student.email = request.form['email']
        student.contact = request.form.get('contact')
        
        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('update_student.html', student=student)



@app.route('/student/<int:student_id>/delete', methods=['GET', 'POST'])
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    # Soft delete
    student.deleted = True
    db.session.commit()
    flash('Student marked as deleted.', 'success')
    return redirect(url_for('index'))

@app.route('/student/<int:student_id>/attendance', methods=['GET', 'POST'])
def manage_attendance(student_id):
    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        att_date = request.form['date']
        status = request.form['status']
        att_date_obj = datetime.strptime(att_date, '%Y-%m-%d').date()

        existing = Attendance.query.filter_by(student_id=student.id, date=att_date_obj).first()
        if existing:
            existing.status = status
        else:
            attendance = Attendance(date=att_date_obj, status=status, student=student)
            db.session.add(attendance)
        db.session.commit()
        flash('Attendance updated!', 'success')
        return redirect(url_for('manage_attendance', student_id=student.id))

    attendance_records = Attendance.query.filter_by(student_id=student.id).order_by(Attendance.date.desc()).all()
    return render_template('attendance.html', student=student, attendance_records=attendance_records, date=date)

@app.route('/student/<int:student_id>/messages', methods=['GET', 'POST'])
def messages(student_id):
    student = Student.query.get_or_404(student_id)
    if request.method == 'POST':
        content = request.form['content']
        sender = request.form['sender']
        if not content or not sender:
            flash('Please provide message content and sender.', 'danger')
            return redirect(url_for('messages', student_id=student.id))
        message = Message(content=content, sender=sender, timestamp=datetime.now(), student=student)
        db.session.add(message)
        db.session.commit()
        flash('Message sent!', 'success')
        return redirect(url_for('messages', student_id=student.id))

    messages = Message.query.filter_by(student_id=student.id).order_by(Message.timestamp.desc()).all()
    return render_template('messages.html', student=student, messages=messages)

@app.route('/search', methods=['GET', 'POST'])
def search_students():
    query = request.args.get('query', '').strip()

    if query:
        if query.isdigit():
            # Search by ID (roll number)
            students = Student.query.filter(
                and_(
                    Student.roll_no == int(query),
                    or_(Student.deleted == False, Student.deleted == None)
                )
            ).all()
        else:
            # Search by name
            students = Student.query.filter(
                and_(
                    Student.name.ilike(f'%{query}%'),
                    or_(Student.deleted == False, Student.deleted == None)
                )
            ).all()
    else:
        # Return all students who are not deleted
        students = Student.query.filter(
            or_(Student.deleted == False, Student.deleted == None)
        ).all()

    return render_template('index.html', students=students, query=query)


if __name__ == '__main__':
    app.run(debug=True)
