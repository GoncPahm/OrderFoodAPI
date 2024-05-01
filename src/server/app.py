from flask import Flask, render_template, request, redirect, url_for, session
from flask_cors import CORS
import os
import pyodbc
from werkzeug.utils import secure_filename
from datetime import timedelta,datetime, timezone
from flask_login import LoginManager, UserMixin, logout_user, login_required, current_user
from user import user, User
from userdetails import user_details
from admin import admin
from cart import cart
from food import food
from order_details import order_details
from order_history import order_history_bp

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

app.permanent_session_lifetime = timedelta(hours=24)


upload = 'E:/OrderFoodAPI/src/assets/imgs/food'
app.config['UPLOAD_FOLDER'] = upload

conn = pyodbc.connect("DRIVER={SQL Server};SERVER=LAPTOP-NIANCD4A\SQLEXPRESS;DATABASE=OrderFood;Trusted_Connection=yes")
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

@app.before_request
def check_session_expiry():
    now = datetime.now(timezone.utc)
    session_modified_time = session.get('_session_modified_time')
    if session_modified_time is not None and (now - session_modified_time) > app.permanent_session_lifetime:
        session.clear()
        logout_user()

@app.route("/", methods=["GET"])
@login_required
def index():
    return render_template("pages/index.html", current_user = current_user)

app.register_blueprint(user)
app.register_blueprint(admin)
app.register_blueprint(user_details)
app.register_blueprint(cart)
app.register_blueprint(food)
app.register_blueprint(order_details)
app.register_blueprint(order_history_bp)

if __name__ == "__main__":
    app.run(debug=True)


