from flask import Flask, render_template, request, redirect, url_for
from flask_cors import CORS
import os
import pyodbc
from flask_login import LoginManager, UserMixin, logout_user, login_required
from user import user, User

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
login_manager.login_view = 'login'


conn = pyodbc.connect("DRIVER={SQL SERVER};SERVER=LAPTOP-O48LC4FO\\QHUY;DATABASE=OrderFood;Trusted_Connection=yes")

cursor = conn.cursor()

@login_manager.user_loader
def load_user(user_id):
    cursor.execute("SELECT * FROM Users WHERE UserID=?", user_id)
    user_data = cursor.fetchone()

    if user_data:
        user_id = user_data[0]
        return User(user_id)

    return redirect(url_for("index"))


@app.route("/", methods=["GET"])
@login_required
def index():
    return render_template("pages/index.html")

@app.route("/checkout", methods=["GET"])
def checkout():
    return render_template("pages/checkout.html")


@app.route("/order-details", methods=["GET"])
def order_detail():
    return render_template("pages/order-details.html")

@app.route("/details", methods=["GET"])
def details():
    return "Details"


app.register_blueprint(user)

if __name__ == "__main__":
    app.run(debug=True)