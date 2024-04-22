from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

db = SQLAlchemy()
admin=Admin()

def teacher_portal():
    app = Flask(__name__, template_folder='templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/test'
    app.secret_key = 'secret key is here'

    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='App', template_mode='bootstrap3')

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    from models import Student, Professor
    
    @login_manager.user_loader
    def load_user(uid):
        student = Student.query.get(uid)
        if student:
            return student
        else:
            professor = Professor.query.get(uid)
            return professor

    bcrypt = Bcrypt(app)

    from routes import register_routes
    register_routes(app, db, bcrypt)
    
    migrate = Migrate(app, db)
    
    from models import Student
    admin.add_view(ModelView(Student, db.session))

    return app