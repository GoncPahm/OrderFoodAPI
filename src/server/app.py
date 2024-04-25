from flask import Flask, render_template, request, redirect, url_for
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import pyodbc
from flask_login import LoginManager, UserMixin, logout_user, login_required, current_user
from user import user, User
from userdetails import user_details


app = Flask(__name__)
app.config['SECRET_KEY'] = 'OrderFoodAPI'

CORS(app)
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets'))

# Đặt đường dẫn cho Flask để tìm kiếm các template, assets
app.template_folder = template_dir
app.static_folder = assets_dir

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user.login'

conn = pyodbc.connect("DRIVER={SQL SERVER};SERVER=LAPTOP-O48LC4FO\\QHUY;DATABASE=OrderFood;Trusted_Connection=yes")
cursor = conn.cursor()

@login_manager.user_loader
def load_user(user_id):
    cursor.execute("SELECT UserID, UserFirstName, UserLastName FROM Users WHERE UserID=?", user_id)
    user_data = cursor.fetchone()

    if user_data:
        user_id = user_data.UserID
        first_name = user_data.UserFirstName
        last_name = user_data.UserLastName
        return User(user_id, first_name, last_name)

    return None


@app.route('/food', methods=["GET"]) 
def query_example(): 
    id = request.args.get('id') 
    return render_template("pages/food-detail.html", id=id, current_user = current_user)

@app.route("/", methods=["GET"])
@login_required
def index():
    return render_template("pages/index.html", current_user = current_user)

@app.route("/order-details", methods=["GET"])
def order_detail():
    return render_template("pages/order-details.html")

@app.route("/details", methods=["GET"])
def details():
    return "Details"

@app.route("/admin", methods=["GET"])
def admin():
    return render_template("admin/layout.html")


upload = 'C:/Python-Code/OrderFoodAPI/src/assets/imgs/food'
app.config['UPLOAD_FOLDER'] = upload

@app.route("/admin/food-manager", methods=["GET", "POST"])
def admin_food():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return render_template("admin/food.html")


@app.route("/admin/order-manager", methods=["GET"])
def admin_order():
    return render_template("admin/order.html")

@app.route("/admin/user-manager", methods=["GET"])
def admin_user():
    return render_template("admin/user.html")


app.register_blueprint(user)
app.register_blueprint(user_details)

if __name__ == "__main__":
    app.run(debug=True)


