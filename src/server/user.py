from flask import Blueprint, request, jsonify, json, redirect, url_for, session
from flask import Flask, render_template, request
from flask_wtf import FlaskForm, csrf
from flask_bcrypt import Bcrypt
from wtforms import StringField, PasswordField, SubmitField, validators
import pyodbc
from flask_login import login_user, logout_user, LoginManager, UserMixin, current_user, login_required

conn = pyodbc.connect("DRIVER={SQL Server};SERVER=LAPTOP-NIANCD4A\SQLEXPRESS;DATABASE=OrderFood;Trusted_Connection=yes")
cursor = conn.cursor()

user = Blueprint("user", __name__)

bcrypt = Bcrypt()
login_manager = LoginManager()

class User(UserMixin):
    def __init__(self, user_id, first_name, last_name):
        self.id = user_id
        self.first_name = first_name
        self.last_name = last_name

    def get_id(self):
        return str(self.id)


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[validators.DataRequired(), validators.Email()],
                        render_kw=
                        {
                            "type":"email",
                            "id":"email-field",
                            "class":"form-control form-control-submit",
                            "placeholder":"Email"
                        })
    password = PasswordField('Password',
                            validators=[validators.DataRequired()],
                            render_kw={
                                "type":"password",
                                "id":"password-field",
                                "class":"form-control form-control-submit",
                                "placeholder":"Password"
                            })
    submit = SubmitField('Sign in',
                        render_kw={
                            "type":"submit",
                            "id":"button-login",
                            "class":"btn-second btn-submit full-width btn-login"
                        })
    
class RegisterForm(FlaskForm):
    first_name = StringField('First Name',
                        validators=[validators.DataRequired()],
                        render_kw=
                        {
                            "type":"text",
                            "id":"first-name-field",
                            "class":"form-control form-control-submit",
                            "placeholder":"First name"
                        })
    last_name = StringField('Last Name',
                        validators=[validators.DataRequired()],
                        render_kw=
                        {
                            "type":"text",
                            "id":"last-name-field",
                            "class":"form-control form-control-submit",
                            "placeholder":"Last name"
                        })
    email = StringField('Email',
                        validators=[validators.DataRequired(), validators.Email()],
                        render_kw=
                        {
                            "type":"email",
                            "id":"email-field",
                            "class":"form-control form-control-submit",
                            "placeholder":"Email"
                        })
    password = PasswordField('Password',
                            validators=[validators.DataRequired()],
                            render_kw={
                                "type":"password",
                                "id":"password-field",
                                "class":"form-control form-control-submit",
                                "placeholder":"Password"
                            })
    submit = SubmitField('Sign up',
                        render_kw={
                            "type":"submit",
                            "id":"button-register",
                            "class":"btn-second btn-submit full-width btn-login"
                        })
    

def authenticate(email, password):
    cursor.execute("SELECT UserID, UserFirstName, UserLastName, UserPassword FROM Users WHERE UserEmail=?", email)
    user_data = cursor.fetchone()
    if user_data:
        
        if bcrypt.check_password_hash(user_data.UserPassword, password):
            user_id = user_data.UserID
            first_name = user_data.UserFirstName
            last_name = user_data.UserLastName
            return User(user_id, first_name, last_name), {}
        else:    
            return None, {"email": "", "password": "Wrong password"}
        
    return None, {"email": "Account isn't registered", "password": ""}


@user.route("/login", methods=["GET"])
def login():
    form = LoginForm()
    return render_template("pages/login.html", form = form)

@user.route("/login", methods=["POST"])
def post_login():
    form = LoginForm()
    if form.validate_on_submit():
        # Xác thực thành công
        email = form.email.data
        password = form.password.data
        try:
            user_login, error_message = authenticate(email, password)
            print(error_message)
            if user_login:
                login_user(user_login)
                session["user_id"] = user_login.get_id()
                return jsonify({"first_name": current_user.first_name, "last_name": current_user.last_name})
            else:
                return jsonify({"errors": error_message})
        except Exception as e:
            print("Error", str(e))
            return jsonify({"errors": "An error occurred while processing your request"}), 500
            
    else:
        errors = form.errors
        return jsonify({ "errors": errors })
    
@user.route("/register", methods=["GET"])
def register():
    form = RegisterForm()
    return render_template("pages/register.html", form = form)

@user.route("/register", methods=["POST"])
def post_register():
    form = RegisterForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = form.password.data
        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

        try:
            cursor.execute("SELECT UserEmail FROM Users WHERE UserEmail = ?", email)
            row = cursor.fetchone()
            if row:
                return jsonify(
                    {
                        "errors":
                        {
                            "first_name": "",
                            "lastname": "",
                            "email": "Email already exists",
                            "password": ""
                        }
                    })
            else:
                cursor.execute("INSERT INTO Users (UserFirstName, UserLastName, UserEmail, UserPassword, UserRole) VALUES (?, ?, ?, ?, ?);",(first_name, last_name, email, password_hash, 0))
                conn.commit()
                return jsonify({"firstname": first_name, "lastname": last_name, "email": email, "password": password})
        except Exception as e:
            print("Error", str(e))
    else:
        errors = form.errors
        return jsonify({ "errors": errors })
    
@user.route("/logout", methods=["GET"])
@login_required
def log_out():
    logout_user()
    return redirect(url_for("index"))
    