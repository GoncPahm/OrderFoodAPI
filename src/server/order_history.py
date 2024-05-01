import pyodbc
import user
from flask_login import current_user, login_required
from flask import Blueprint, jsonify, render_template

order_history_bp = Blueprint('order_history_bp', __name__)


conn = pyodbc.connect("DRIVER={SQL Server};SERVER=LAPTOP-NIANCD4A\SQLEXPRESS;DATABASE=OrderFood;Trusted_Connection=yes")
cursor = conn.cursor()


def get_order_history(userId):
    try:
        query = """
        SELECT Orders.OrderID, OrderDate, SUM(OrderItems.OrderQuantity * CAST(Food.FoodPrice AS INT) * (1 - ISNULL(Food.FoodDiscount, 0)/100.0)) AS TotalPrice
        FROM Orders
        JOIN OrderItems ON Orders.OrderID = OrderItems.OrderID
        JOIN Food ON OrderItems.FoodID = Food.FoodID
        WHERE Orders.UserID = ?
        GROUP BY Orders.OrderID, OrderDate
        """
        cursor.execute(query, userId)
        data = []
        columns = [column[0] for column in cursor.description]
        values = cursor.fetchall()
        for value in values:
            data.append(dict(zip(columns, value)))
        return data
    except Exception as e:
        print(f"Error while getting user data: {e}")
        return []


@order_history_bp.route("/order-history", methods=["GET"])
@login_required
def order_history():
    return render_template("pages/order-history.html")


@order_history_bp.route('/api/order-history', methods=['GET'])
def get_order_historys():
    userId = current_user.get_id()
    data_history = get_order_history(userId)
    return jsonify(data_history)