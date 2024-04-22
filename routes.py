from flask import render_template, request, flash, redirect, url_for, flash
from flask_login import login_user, login_required, current_user, logout_user
from models import Student, Professor
from sqlalchemy.sql import text


def register_routes(app, db, bcrypt):

    @app.route("/")
    def home():
        if current_user.is_authenticated:
            if isinstance(current_user, Student):
                return redirect((url_for('student_dashboard')))
            elif isinstance(current_user, Professor):
                return redirect((url_for('professor_dashboard')))
        return redirect((url_for('login')))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "GET":
            return render_template('login.html')  
        elif request.method == "POST":
            email = request.form['email']
            password = request.form['password']
            user_type = request.form.get('user-type-value') 
    
            if user_type == "student":
                student = Student.query.filter(Student.email==email).first()
                if student and bcrypt.check_password_hash(student.password, password):
                    login_user(student)
                    flash("Login successful!", 'success')  
                    return redirect((url_for('student_dashboard')))
                else:
                    flash("Incorrect email or password for student. Please try again.", 'danger')

            elif user_type == "professor":
                professor = Professor.query.filter(Professor.email==email).first()
                if professor and bcrypt.check_password_hash(professor.password, password):
                    login_user(professor)
                    flash("Login successful!", 'success')  
                    return redirect(url_for('professor_dashboard'))
                else:
                    flash("Incorrect email or password for professor. Please try again.", 'danger')
        
        return redirect((url_for('login')))

    @app.route("/student-dashboard")
    def student_dashboard():
        if isinstance(current_user, Student):
            courses_enrolled = Student.query.filter(Student.student_id==current_user.student_id).first().courses
            student_info = {}
            for course in courses_enrolled:
                course_name = course.course_name
                course_id = course.course_id
                professor_data = db.session.execute(text("""SELECT professors.name, professors.email FROM professors JOIN student_professor ON professors.professor_id = student_professor.professor_id 
                                        JOIN students ON students.student_id = student_professor.student_id
                                        JOIN courses ON professors.course_id = courses.course_id
                                        WHERE students.student_id = :student_id AND courses.course_id = :course_id;"""), { "student_id": current_user.student_id, "course_id": course_id}).fetchall()
                attendance_count = db.session.execute(text("""SELECT count FROM attendance WHERE student_id=:student_id AND course_id=:course_id"""), { "student_id": current_user.student_id, "course_id": course_id}).fetchall()
                grade = db.session.execute(text("""SELECT grade FROM grades WHERE student_id=:student_id AND course_id=:course_id"""), { "student_id": current_user.student_id, "course_id": course_id}).fetchall()
                student_info[course_name] = {
                    'professor_data': professor_data,
                    'attendance_count': attendance_count,
                    'grade': grade
                }
            return render_template('student-dashboard.html',  msg="Student", student_info=student_info)
        elif isinstance(current_user, Professor):
            flash("Professors can not access this page.", 'danger')  
            return redirect((url_for('professor_dashboard')))
        else:
            return redirect((url_for('login')))
        
    @app.route("/professor-dashboard")
    def professor_dashboard():
        if isinstance(current_user, Professor):
            students = Professor.query.filter(Professor.professor_id==current_user.professor_id).first().students
            professor_info = {}
            for student in students:
                student_id = student.student_id
                student_name = student.name
                attendance_count = db.session.execute(text("""SELECT count FROM attendance WHERE student_id=:student_id AND course_id=:course_id"""), { "student_id": student.student_id, "course_id": current_user.course_id}).fetchall()
                grade = db.session.execute(text("""SELECT grade FROM grades WHERE student_id=:student_id AND course_id=:course_id"""), { "student_id": student.student_id, "course_id": current_user.course_id}).fetchall()
                student_contact = student.email
                professor_info[student_id] = {
                    'student_name': student_name,
                    'student_id': student_id,
                    'attendance_count': attendance_count,
                    'grade': grade,
                    'student_contact': student_contact
                }
            return  render_template('professor-dashboard.html', msg="Professor",professor_info=professor_info)
        elif isinstance(current_user, Student):
            flash("Students can not access this page.", 'danger')  
            return redirect((url_for('student_dashboard')))
        else:
            return redirect((url_for('login')))
        
    @app.route("/register-professor", methods=["GET", "POST"])
    def register_professor():
        if isinstance(current_user, Professor):
            if request.method == "GET":
                courses =  db.session.execute(text('SELECT * FROM courses;')).fetchall()
                print(courses)
                return render_template('register-professor.html', msg="Professor", courses=courses)
            elif request.method == "POST":
                name = request.form['name']
                email = request.form['email']
                password = request.form['password']
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                course_id = request.form['course_id']
                professor_exist = Professor.query.filter(Professor.email==email).first()
                
                if professor_exist:
                    flash("Professor already exists. Please try enrolling the student.", 'danger')
                    return redirect((url_for('professor_dashboard')))
                
                last_professor = Professor.query.filter(Professor.professor_id.like(f'{course_id}%')).order_by(Professor.professor_id.desc()).first()
                if last_professor is None:
                    professor_id = int(f'{course_id}00001')
                else:
                    professor_id = last_professor.professor_id + 1
                professor = Professor(professor_id=professor_id, name=name, email=email, password=hashed_password, course_id=course_id)
                db.session.add(professor)
                db.session.commit()
                return redirect((url_for('register_professor')))
        elif isinstance(current_user, Student):
            flash("Students can not access this page.", 'danger')  
            return redirect((url_for('student-dashboard')))
        else:
            return redirect((url_for('login')))
    
    @app.route("/enroll-student", methods=["GET", "POST"])
    def enroll_student():
        if isinstance(current_user, Professor):
            if request.method == "GET":
                enrolled_students = Professor.query.filter(Professor.professor_id==current_user.professor_id).first().students
                enrolled_students_ids =[student.student_id for student in enrolled_students]
                if enrolled_students_ids:
                    unenrolled_students = db.session.execute(text("""SELECT student_id, name, email FROM students WHERE student_id NOT IN :enrolled_students_ids;"""), { "enrolled_students_ids": enrolled_students_ids}).fetchall()
                else:
                    unenrolled_students = db.session.execute(text("""SELECT student_id, name, email FROM students""")).fetchall()
                student_info = {}
                for student in unenrolled_students:
                    student_id = student.student_id
                    student_name = student.name
                    student_email = student.email
                    student_info[student_id] = {
                        'student_name': student_name,
                        'student_email': student_email
                    }
                return render_template('enroll-student.html', msg="Professor", student_info=student_info)
            elif request.method == "POST":
                student_ids = request.form.getlist('enroll_students')
                for student_id in student_ids:
                    db.session.execute(text("""INSERT INTO enrollments (student_id, course_id) VALUES (:student_id, :course_id)"""), { "student_id": student_id, "course_id": current_user.course_id})
                    db.session.execute(text("""INSERT INTO attendance (student_id, course_id, count) VALUES (:student_id, :course_id, :count)"""), { "student_id": student_id, "course_id": current_user.course_id, "count": 0})
                    db.session.execute(text("""INSERT INTO grades (student_id, course_id, grade) VALUES (:student_id, :course_id, :grade)"""), { "student_id": student_id, "course_id": current_user.course_id, "grade": 'N/A'})
                    db.session.execute(text("""INSERT INTO student_professor (student_id, professor_id) VALUES (:student_id, :professor_id)"""), { "student_id": student_id, "professor_id": current_user.professor_id})
                    db.session.commit()
                flash("Students enrolled successfully", 'success')
                return redirect((url_for('professor_dashboard')))
        elif isinstance(current_user, Student):
            flash("Students can not access this page.", 'danger')  
            return redirect((url_for('student-dashboard')))
        else:
            return redirect((url_for('login')))
    
    @app.route("/register-student", methods=["GET", "POST"])
    def register_student():
        if isinstance(current_user, Professor):
            if request.method == "GET":
                return render_template('register-student.html', msg="Professor")
            elif request.method == "POST":
                name = request.form['name']
                email = request.form['email']
                password = request.form['password']
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')               
                student_exist = Student.query.filter(Student.email==email).first()
                
                if student_exist:
                    flash("Student already exists. Please try enrolling the student.", 'danger')
                    return redirect((url_for('professor_dashboard')))                
                
                last_student = Student.query.filter(Student.student_id.like(f'24%')).order_by(Student.student_id.desc()).first()
                if last_student is None:
                    student_id = int(f'2400001')
                else:
                    student_id = last_student.student_id + 1
                student = Student(student_id=student_id, name=name, email=email, password=hashed_password)
                db.session.add(student)
                db.session.commit()
                db.session.execute(text("""INSERT INTO enrollments (student_id, course_id) VALUES (:student_id, :course_id)"""), { "student_id": student_id, "course_id": current_user.course_id})
                db.session.execute(text("""INSERT INTO attendance (student_id, course_id, count) VALUES (:student_id, :course_id, :count)"""), { "student_id": student_id, "course_id": current_user.course_id, "count": 0})
                db.session.execute(text("""INSERT INTO grades (student_id, course_id, grade) VALUES (:student_id, :course_id, :grade)"""), { "student_id": student_id, "course_id": current_user.course_id, "grade": 'N/A'})
                db.session.execute(text("""INSERT INTO student_professor (student_id, professor_id) VALUES (:student_id, :professor_id)"""), { "student_id": student_id, "professor_id": current_user.professor_id})
                db.session.commit()
                return redirect((url_for('professor_dashboard')))
        elif isinstance(current_user, Student):
            flash("Students can not access this page.", 'danger')  
            return redirect((url_for('student-dashboard')))
        else:
            return redirect((url_for('login')))
        
    @app.route("/edit-student/<student_id>", methods=["GET", "POST"])
    def edit_student(student_id):
        if isinstance(current_user, Professor):
            students = Professor.query.filter(Professor.professor_id==current_user.professor_id).first().students
            for student in students:
                if int(student.student_id) == int(student_id):                    
                    if request.method == "GET":
                        attendance_count = db.session.execute(text("""SELECT count FROM attendance WHERE student_id=:student_id AND course_id=:course_id"""), { "student_id": student.student_id, "course_id": current_user.course_id}).fetchall()
                        grade = db.session.execute(text("""SELECT grade FROM grades WHERE student_id=:student_id AND course_id=:course_id"""), { "student_id": student.student_id, "course_id": current_user.course_id}).fetchall()
                        return render_template('edit-student.html', msg="Professor", student_id=student_id, student_name=student.name, student_email=student.email, attendance_count=attendance_count, grade=grade)
                    elif request.method == "POST":
                        name = request.form['name']
                        email = request.form['email']
                        attendance_count = request.form['attendance_count']
                        grade = request.form['grade']
                        db.session.execute(text("""UPDATE students SET name=:name, email=:email WHERE student_id=:student_id"""), { "name": name, "email": email, "student_id": student.student_id})
                        db.session.execute(text("""UPDATE grades SET grade=:grade WHERE student_id=:student_id AND course_id=:course_id"""), { "grade": grade, "student_id": student.student_id, "course_id": current_user.course_id})
                        db.session.execute(text("""UPDATE attendance SET count=:count WHERE student_id=:student_id AND course_id=:course_id"""), { "count": attendance_count, "student_id": student.student_id, "course_id": current_user.course_id})
                        db.session.commit()                    
                        return redirect((url_for('professor_dashboard')))
                else:
                    continue
        elif isinstance(current_user, Student):
            flash("Students can not access this page.", 'danger')  
            return redirect((url_for('student-dashboard')))
        else:
            return redirect((url_for('login')))

    @app.route("/edit-user", methods=["GET", "POST"])
    def edit_user():
        if isinstance(current_user, Professor):
            if request.method == "GET":
                return render_template('edit-user.html')
            elif request.method == "POST":
                name = request.form['name']
                email = request.form['email']
                old_password = request.form['old-password']
                new_password = request.form['new-password']
                db.session.execute(text("""UPDATE professors SET name=:name, email=:email WHERE professor_id=:professor_id"""), { "name": name, "email": email, "professor_id": current_user.professor_id})
                db.session.commit()     
                if new_password: 
                    if bcrypt.check_password_hash(current_user.password, old_password):
                        hashed_new_password = bcrypt.generate_password_hash(new_password).decode('utf-8') 
                        db.session.execute(text("""UPDATE professors SET password=:hashed_new_password WHERE professor_id=:professor_id"""), { "hashed_new_password": hashed_new_password,"professor_id": current_user.professor_id})
                        db.session.commit()     
                        flash("Changes were saved successfully!", 'success')
                        return redirect(url_for('professor_dashboard'))
                    else:
                        flash("Couldn't update password!", 'danger')
                        return redirect(url_for('professor_dashboard'))
                else:
                    flash("Changes were saved successfully!", 'success')
                    return redirect(url_for('professor_dashboard'))
        elif isinstance(current_user, Student):
            if request.method == "GET":
                return render_template('edit-user.html')
            elif request.method == "POST":
                name = request.form['name']
                email = request.form['email']
                old_password = request.form['old-password']
                new_password = request.form['new-password']
                db.session.execute(text("""UPDATE students SET name=:name, email=:email WHERE student_id=:student_id"""), { "name": name, "email": email, "student_id": current_user.student_id})
                db.session.commit()     
                if new_password: 
                    if bcrypt.check_password_hash(current_user.password, old_password):
                        hashed_new_password = bcrypt.generate_password_hash(new_password).decode('utf-8') 
                        db.session.execute(text("""UPDATE students SET password=:hashed_new_password WHERE student_id=:student_id"""), { "hashed_new_password": hashed_new_password,"student_id": current_user.student_id})
                        db.session.commit()     
                        flash("Changes were saved successfully!", 'success')
                        return redirect(url_for('student_dashboard'))
                    else:
                        flash("Couldn't update password!", 'danger')
                        return redirect(url_for('student_dashboard'))
                else:
                    flash("Changes were saved successfully!", 'success')
                    return redirect(url_for('student_dashboard'))
        else:
            return redirect((url_for('login')))
            
   
    @app.route("/delete-student", methods=["POST"])
    @login_required
    def delete_student():
        if isinstance(current_user, Professor):
            student_id = request.form['student_id']
            db.session.execute(text("""DELETE FROM student_professor WHERE student_id=:student_id AND professor_id=:course_id"""), { "student_id": student_id, "course_id": current_user.professor_id})
            db.session.commit()
            return redirect(url_for('professor_dashboard'))
        elif isinstance(current_user, Student):
            flash("Students can not access this page.", 'danger')  
            return redirect((url_for('student-dashboard')))
        else:
            return redirect((url_for('login')))

    @app.route("/logout")
    @login_required 
    def logout():
        logout_user()
        flash("User logged out successfully!", 'success')
        return redirect(url_for('login'))