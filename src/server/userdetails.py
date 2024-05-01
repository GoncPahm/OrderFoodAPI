import pyodbc
from wtforms import SubmitField,StringField,validators
from flask_wtf import FlaskForm
from flask import Blueprint, jsonify, request, render_template, redirect, url_for
from flask_login import current_user, login_required
from flask_bcrypt import Bcrypt
user_details = Blueprint("user_details", __name__)

conn = pyodbc.connect("DRIVER={SQL Server};SERVER=LAPTOP-NIANCD4A\SQLEXPRESS;DATABASE=OrderFood;Trusted_Connection=yes")
cursor = conn.cursor()

cursor_food = conn.cursor()

@user_details.route('/checkout', methods=['GET'])
@login_required
def checkout():
    try:
        userID = current_user.get_id()
        print(userID)
        cursor.execute("SELECT * FROM UserDetails WHERE UserID = ?", userID)
        user_data = cursor.fetchone()
        cursor_food.execute("SELECT  Food.FoodName , CartItems.CartItemQuantity, Food.FoodImage, Food.FoodDiscount, Food.FoodPrice, Food.FoodID , CartItems.UserID,(CartItems.CartItemQuantity * CAST(Food.FoodPrice AS INT) * (1 - ISNULL(Food.FoodDiscount,0)/100.0)) AS TotalPrice  FROM CartItems  JOIN Food ON CartItems.FoodID = Food.FoodID   WHERE CartItems.UserID = ?", userID)
        cart_items = cursor_food.fetchall()
        print("HAHAH", cart_items)
        if user_data:
            return render_template("pages/checkout.html",data = user_data, cart_items = cart_items, userID = userID)
        else:
            return render_template("pages/checkout.html", data = {},cart_items = cart_items, userID = userID)
    except Exception as e:
        return jsonify({'success': False})
    

def c_t_p(cart_items):
    if not cart_items:
        return 0 
    total_price = sum(item.TotalPrice for item in cart_items if item)
    return total_price

@user_details.route('/checkout/delete-cart-item/<int:food_id>', methods=['DELETE'])
@login_required
def delete_cart_item(food_id):
    try:
        user_id = current_user.get_id()
        cursor.execute("DELETE FROM CartItems WHERE UserID = ? AND FoodID = ?", (user_id, food_id))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False})

@user_details.route('/update-user-details', methods=['PUT'])
@login_required
def update_user_details():
    try:
        userID = current_user.get_id()
        user_data = request.json
        UserName = user_data.get('UserName')
        UserAddress = user_data.get('UserAddress')
        UserTel = user_data.get('UserTel')
        UserCredit = user_data.get('UserCredit')
        
        cursor.execute("SELECT * FROM UserDetails WHERE UserID = ?", userID)
        data = cursor.fetchone()
        if data:
            cursor.execute(" UPDATE UserDetails SET UserAddress = ?, UserName = ?, UserTel = ?, UserCredit = ?   WHERE UserID = ?", (UserAddress, UserName, UserTel, UserCredit, userID))
            conn.commit()
        else:
            cursor.execute("insert into UserDetails (UserID, UserAddress, UserName, UserTel, UserCredit) values(?,?,?,?,?) ;",(userID, UserAddress, UserName, UserTel, UserCredit))
            conn.commit()        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False})
    
@user_details.route('/place-order', methods=['POST'])
@login_required
def place_order():
    try:
        order_data = request.json
        user_id = current_user.get_id()
        order_date = order_data.get('OrderDate')
        order_status = order_data.get('OrderStatus')
        order_payment = order_data.get('OrderPayment')
        order_items = order_data.get('OrderItems')

        order_nameus = order_data.get('UserName')
        order_addressus = order_data.get('UserAddress')
        order_telus = order_data.get('UserTel')
        
        # Insert order and items
        order_result = insert_order_and_items(user_id, order_date, order_status, order_payment, order_items)
        if not order_result['success']:
            return jsonify(order_result)
        
        order_id = order_result['order_id']
        
        # Insert user details
        user_details_result = insert_user_details(user_id, order_id, order_nameus, order_addressus, order_telus)
        if not user_details_result['success']:
            return jsonify(user_details_result)
        
        # Delete all items in cart
        cart_result = delete_all_items_in_cart()
        if not cart_result['success']:
            return jsonify(cart_result)
        
        return jsonify({'success': True, 'order_id': order_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def insert_order_and_items(user_id, order_date, order_status, order_payment, order_items):
    try:
        cursor.execute(" INSERT INTO Orders (UserID, OrderDate, OrderStatus, OrderPayment) OUTPUT INSERTED.OrderID  VALUES (?, ?, ?, ?)", (user_id, order_date, order_status, order_payment))
        order_id = cursor.fetchone()[0]
        
        if not order_id:
            raise Exception('Error: OrderID not retrieved.')
        
        for item in order_items:
            food_id = item['FoodID']
            order_quantity = item['OrderQuantity']
            cursor.execute("INSERT INTO OrderItems (OrderID, FoodID, OrderQuantity)  VALUES (?, ?, ?)", (order_id, food_id, order_quantity))
        
        conn.commit()
        
        return {'success': True, 'order_id': order_id}
    except Exception as e:
        conn.rollback()
        return {'success': False, 'error': str(e)}

def delete_all_items_in_cart():
    try:
        user_id = current_user.get_id()
        
        cursor.execute("DELETE FROM CartItems WHERE UserID=?",user_id) 
        conn.commit()
        
        return {'success': True}
    except Exception as e:
        
        conn.rollback()
        return {'success': False}
    
def insert_user_details(user_id, order_id, detail_name, detail_address, detail_tel):
    try:
        cursor.execute(" INSERT INTO OrderUserDetails (UserID, OrderID, DetailName, DetailAddress, DetailTel) VALUES (?, ?, ?, ?, ?) ", (user_id, order_id, detail_name, detail_address, detail_tel))
        
        conn.commit()
        
        return {'success': True}
    except Exception as e:
        conn.rollback()
        
        return {'success': False, 'error': str(e)}