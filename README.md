# Student Management Portal (MUJ version)
Welcome to the Student Management Portal! 

## Features
- Register and login professors and students.
- Enroll students in courses.
- Dashboard for professors to record attendance and grades of their students.
- Dashboard for students to view the grades and attendance.

## Technologies Used
- MySQL: An open-source  relational database management system to manage all the data.
- Flask: A lightweight web application framework used for the backend.
- Bootstrap: A front-end framework for building responsive and visually appealing web pages.
- Font Awesome: A library of icons used for enhancing the UI.
- Jinja Templating: A template engine for Python used with Flask for generating dynamic HTML content.

## Requirement
1. **Python version 3.12 which can be installed [here](https://www.python.org/downloads/release/python-3123/)**
2. **MySQL version 8.3 which can be installed [here](https://dev.mysql.com/downloads/mysql/)**
## Setup

1. **Clone the repository**
2. **Navigate to the project directory**
3. **Create and activate a virtual environment for your project:**  
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
3. **Install the python requirements:**
  ```
pip install -r requiremnts.txt
  ```
4. **Set up the database:**
- Create a database you want to connect this app to.
- Change the database uri credentials in run.py
- Run the following commands to initialize the database:
  ```
  flask db init
  flask db migrate
  flask db upgrade
  ```
- Now create a new professors record manually and make sure to store the hashed password in the password column.

5. **Run the application:**
```
python .\app.py
```
6. **Access the application:**
- Open a web browser and navigate to `http://localhost:5000`.

## Usage

- Upon running the application, you will be directed to the login page.
- Log in as a professor using the credentials created.
- Once logged in, you can navigate through the different pages to manage students, professors, courses, attendance, and grades.

## Future Add-ons

- Assigning classes to students 
- Implement pagination for better navigation through large lists of students or courses.
- Enhance the UI with more interactive features and animations.
- Add support for generating reports or analytics on student performance.

## Contributing

Contributions are welcome! If you find any bugs or have suggestions for new features, please open an issue or submit a pull request.
