from run import teacher_portal

flask_app = teacher_portal()

if __name__ == '__main__':
    flask_app.run(debug=True)
