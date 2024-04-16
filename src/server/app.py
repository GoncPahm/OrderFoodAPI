from flask import Flask, render_template
from flask_cors import CORS
import os
app = Flask(__name__)

CORS(app)

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets'))


# Đặt đường dẫn cho Flask để tìm kiếm các template, assets
app.template_folder = template_dir
app.static_folder = assets_dir

@app.route("/", methods=["GET"])
def index():
    return render_template("pages/index.html")

@app.route("/checkout", methods=["GET"])
def checkout():
    return render_template("pages/checkout.html")

@app.route("/login", methods=["GET"])
def login():
    return render_template("pages/login.html")

@app.route("/register", methods=["GET"])
def register():
    return render_template("pages/register.html")

@app.route("/order-details", methods=["GET"])
def order_detail():
    return render_template("pages/order-details.html")

if __name__ == "__main__":
    app.run(debug=True)