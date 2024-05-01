from flask import jsonify, request, Blueprint
import pyodbc
cart = Blueprint("cart", __name__)

conn = pyodbc.connect("DRIVER={SQL Server};SERVER=LAPTOP-NIANCD4A\SQLEXPRESS;DATABASE=OrderFood;Trusted_Connection=yes")
cursor = conn.cursor()

@cart.route("/cart/<int:user_id>", methods=['GET'])
def get_cart_items(user_id):
    try:
        cursor = conn.cursor()
        cursor.execute("select *, "
                       "ROUND(CAST(foodPrice AS INT) * (100 - ISNULL(FoodDiscount, 0)) / 100, 0) AS newPrice  "
                       "from CartItems "
                       "join Food on CartItems.FoodID = Food.FoodID "
                       "where UserID = ?", user_id)
        result = []
        keys = []
        for i in cursor.description:
            keys.append(i[0])
        for val in cursor.fetchall():
            result.append(dict(zip(keys, val)))
        resp = jsonify(result)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)

@cart.route("/add-cart", methods=['POST'])
def add_cart():
    try:
        user_id = request.json.get("userId")
        food_id = request.json.get("foodId")
        quantity = request.json.get('quantity')
        cursor = conn.cursor()
       
        cursor.execute("insert into CartItems values(?, ?, ?)", user_id, food_id, quantity)
        conn.commit()
        resp = jsonify(
            {
                "id": user_id,
                "food-id": food_id,
                "status": 'added'
            })
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)

@cart.route("/remove-cart", methods=['DELETE'])
def remove_cart():
    try:
        user_id = request.json.get("userId")
        food_id = request.json.get("foodId")
        cursor = conn.cursor()
        cursor.execute("delete CartItems where UserID = ? and FoodID = ?", user_id, food_id)
        conn.commit()
        resp = jsonify(
            {
                "id": user_id,
                "food-id": food_id,
                "status": 'remove'
            })
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)