import pyodbc
from flask_login import current_user, login_required
from flask import Blueprint, jsonify, render_template

order_details = Blueprint('order_details', __name__)

conn = pyodbc.connect("DRIVER={SQL Server};SERVER=LAPTOP-NIANCD4A\SQLEXPRESS;DATABASE=OrderFood;Trusted_Connection=yes")
cursor = conn.cursor()



def get_user_data(userId):
    try:
        sql_query = """
        SELECT TOP 1
            oud.DetailName, 
            oud.DetailAddress, 
            oud.DetailTel
            FROM OrderUserDetails oud
            WHERE oud.UserID = ?
            ORDER BY oud.OrderID DESC
        """
        cursor.execute(sql_query, userId)
        data = []
        columns = [column[0] for column in cursor.description]
        values = cursor.fetchall()
        for value in values:
            data.append(dict(zip(columns, value)))
        return data
    except Exception as e:
        print(f"Error while getting user data: {e}")
        return []
    

def get_user_details(userId, orderId):
    try:
        sql_query = """
            oud.DetailName, 
            oud.DetailAddress, 
            oud.DetailTel
            FROM OrderUserDetails oud
            WHERE oud.UserID = ? and oud.OrderID = ?
        """
        cursor.execute(sql_query, userId, orderId)
        data = []
        columns = [column[0] for column in cursor.description]
        values = cursor.fetchall()
        for value in values:
            data.append(dict(zip(columns, value)))
        return data
    except Exception as e:
        print(f"Error while getting user data: {e}")
        return []

def get_food_data(userId):
    try:
        sql_query = """
        SELECT 
            u.UserID, 
            o.OrderID, 
            o.OrderDate, 
            oi.OrderQuantity, 
            f.FoodName, 
            f.FoodImage, 
            f.FoodDiscount, 
            f.FoodPrice, 
            o.OrderPayment, 
            (oi.OrderQuantity * CAST(f.FoodPrice AS INT) * (1 - ISNULL(f.FoodDiscount,0)/100.0)) AS totalPrice
        FROM 
            Users u
        JOIN 
            Orders o ON u.UserID = o.UserID
        JOIN 
            OrderItems oi ON o.OrderID = oi.OrderID
        JOIN 
            Food f ON oi.FoodID = f.FoodID
        WHERE 
            o.OrderID = (SELECT TOP 1 OrderID FROM Orders WHERE UserID = u.UserID ORDER BY OrderID DESC)
        AND 
            u.UserID = ?
        """

        cursor.execute(sql_query, userId)
        data = []
        columns = [column[0] for column in cursor.description]
        values = cursor.fetchall()
        for value in values:
            data.append(dict(zip(columns, value)))
        return data
    except Exception as e:
        print(f"Error while getting user data: {e}")
        return []

def calculate_total_price(food_data):
    if not food_data:
        return 0 

    total_price = sum(item.get('totalPrice', 0) for item in food_data if item)
    return total_price

def get_data_history(orderId, userId):
    try:
        cursor.execute("select Orders.OrderID, OrderPayment, OrderDate, OrderItems.OrderQuantity, FoodName, FoodImage, FoodPrice, (OrderItems.OrderQuantity * CAST(Food.FoodPrice AS INT) * (1 - ISNULL(Food.FoodDiscount,0)/100.0)) AS totalPrice from Orders join OrderItems on Orders.OrderID = OrderItems.OrderID join Food on OrderItems.FoodID = Food.FoodID where Orders.OrderID = ? and Orders.UserID = ?", orderId, userId)
        data = []
        columns = [column[0] for column in cursor.description]
        values = cursor.fetchall()
        for value in values:
            data.append(dict(zip(columns, value)))
        return data
    except Exception as e:
        print(f"Error while getting user data: {e}")
        return []


@order_details.route("/order-details", methods=["GET"])
@login_required
def order_detailss():
    userId = current_user.get_id()
    food_data = get_food_data(userId)
    totalPrice = calculate_total_price(food_data)
    return render_template("pages/order-details.html", food_data=food_data, totalPrice=totalPrice)

orderId = 0

@order_details.route('/order-details/<int:order_id>', methods=["GET"])
@login_required
def order_detail_history(order_id):
    userId = current_user.get_id()
    orderId = order_id
    food_data_history = get_data_history(order_id, userId)
    totalPrice = calculate_total_price(food_data_history)
    return render_template('pages/order-details.html', food_data = food_data_history, totalPrice = totalPrice)


@order_details.route("/api/order-details-data", methods=["GET"])
@login_required
def api_order_details_data():
    userId = current_user.get_id()
    if orderId:
        user_data = get_user_details(userId, orderId)
    else:
        user_data = get_user_data(userId)
    return jsonify({
        "user_data": user_data
    })