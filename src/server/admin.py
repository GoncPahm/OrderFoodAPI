from flask import render_template, redirect, url_for, Blueprint, jsonify, json
import pyodbc
from flask_wtf import FlaskForm, csrf
from wtforms import StringField, PasswordField, SubmitField, validators, SelectField, DateTimeLocalField
import pyodbc

conn = pyodbc.connect("DRIVER={SQL Server};SERVER=LAPTOP-NIANCD4A\SQLEXPRESS;DATABASE=OrderFood;Trusted_Connection=yes")
cursor = conn.cursor()

admin = Blueprint("admin", __name__)


class UpdateUserForm(FlaskForm):
    UserID = StringField('UserID',
                            validators=[validators.DataRequired()],
                            render_kw={
                                "type":"text",
                                "id":"user-id-field",
                                "class":"form-control form-control-submit disabled",
                                "placeholder":"UserID"
                            })
    UserFirstName = StringField('UserFirstName',
                            validators=[validators.DataRequired()],
                            render_kw={
                                "type":"text",
                                "id":"user-firstname-field",
                                "class":"form-control form-control-submit",
                                "placeholder":"UserFirstName"
                            })
    UserLastName = StringField('UserID',
                            validators=[validators.DataRequired()],
                            render_kw={
                                "type":"text",
                                "id":"user-lastname-field",
                                "class":"form-control form-control-submit",
                                "placeholder":"UserLastName"
                            })
    UserEmail = StringField('UserEmail',
                        validators=[validators.DataRequired(), validators.Email()],
                        render_kw=
                        {
                            "type":"email",
                            "id":"user-email-field",
                            "class":"form-control form-control-submit",
                            "placeholder":"Email"
                        })
    submit = SubmitField('Update',
                        render_kw={
                            "type":"submit",
                            "id":"button-update",
                            "class":"btn-second btn-google mb-2"
                        })

@admin.route("/admin", methods=["GET"])
def admin_index():
    try:
        cursor.execute("Select * FROM Food")
        data = []
        columns = []
        values = cursor.fetchall()
        for column in cursor.description:
            columns.append(column[0])
        for value in values:
            data.append(dict(zip(columns, value)))
        return render_template("admin/index.html", products = data)
    except Exception as e:
        return jsonify({"Errors Admin Get All" : str(e)})
    
    return render_template("admin/index.html", products = [])


@admin.route("/admin/order-manager", methods=["GET"])
def admin_order():
    try:
        cursor.execute("Select * FROM Orders")
        data = []
        columns = []
        values = cursor.fetchall()
        for column in cursor.description:
            columns.append(column[0])
        for value in values:
            data.append(dict(zip(columns, value)))

        print(data)
        return render_template("admin/order.html", orders = data)
    except Exception as e:
        return jsonify({"Errors Admin Get All" : str(e)})
    
    return render_template("admin/order.html", orders = [])


@admin.route("/admin/user-manager", methods=["GET"])
def admin_user():
    form = UpdateUserForm()
    try:
        cursor.execute("Select * FROM Users")
        data = []
        columns = []
        values = cursor.fetchall()
        for column in cursor.description:
            columns.append(column[0])
        for value in values:
            data.append(dict(zip(columns, value)))

        return render_template("admin/user.html",form = form)
    except Exception as e:
        return jsonify({"Errors Admin Get All" : str(e)})
    
    return render_template("admin/user.html", users = [], form = form)

@admin.route('/get_all_user', methods=["GET"])
def get_all_user():
    try:
        cursor.execute("Select * FROM Users")
        data = []
        columns = []
        values = cursor.fetchall()
        for column in cursor.description:
            columns.append(column[0])
        for value in values:
            data.append(dict(zip(columns, value)))
        return jsonify({"users": data})
    except Exception as e:
        return jsonify({"Errors Admin Get User" : str(e)})

@admin.route('/get_user/<user_id>', methods=["GET"])
def get_user(user_id):
    try:
        cursor.execute("Select * FROM Users Where UserID = ?", user_id)
        data = []
        columns = []
        values = cursor.fetchall()
        for column in cursor.description:
            columns.append(column[0])
        for value in values:
            data.append(dict(zip(columns, value)))
        return jsonify({"user": data})
    except Exception as e:
        return jsonify({"Errors Admin Get User" : str(e)})
    
@admin.route('/update_user/<user_id>', methods=["PUT"])
def update_user(user_id):
    form = UpdateUserForm()
    try:
        if form.validate_on_submit():
            first_name = form.UserFirstName.data
            last_name = form.UserLastName.data
            email = form.UserEmail.data
            cursor.execute("update Users set UserFirstName=?, UserLastName=?, UserEmail=? where UserID = ?", (first_name, last_name, email , user_id))
            conn.commit()
            return jsonify({"success": True})
        else:
            errors = form.errors
            return jsonify({"errors": errors})
    except Exception as e:
        return jsonify({"Errors Admin Get User" : str(e)})
