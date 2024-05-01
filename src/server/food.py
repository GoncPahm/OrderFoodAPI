from flask import jsonify, request, Blueprint, render_template
import pyodbc
food = Blueprint("food", __name__)


conn = pyodbc.connect("DRIVER={SQL Server};SERVER=LAPTOP-NIANCD4A\SQLEXPRESS;DATABASE=OrderFood;Trusted_Connection=yes")
cursor = conn.cursor()

@food.route("/food/", methods=["GET"])
def food_index():
    id = request.args.get("id")
    return render_template("pages/food-detail.html", id = id)
    

@food.route("/get_food/", methods=['GET'])
def get_list_food():
    try:
        cursor = conn.cursor()
        cursor.execute("Select * from food")
        print("HIHI")
        result = []
        keys = []
        for i in cursor.description:
            keys.append(i[0])
        for val in cursor.fetchall():
            result.append(dict(zip(keys,val)))
        resp = jsonify(result)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)



@food.route("/get_food/<name>", methods=['GET'])
def get_food_by_name(name):
    try:
        cursor = conn.cursor()
        cursor.execute("Select * from food where foodName like ?", u'%' + name + '%',)
        result = []
        keys = []
        for i in cursor.description:
            keys.append(i[0])
        for val in cursor.fetchall():
            result.append(dict(zip(keys, val)))
        resp=jsonify(result)
        resp.status_code=200
        return resp
    except Exception as e:
        print(e)



@food.route("/food_details/<int:id>", methods=['GET'])
def get_food_by_id(id):
    try:
        cursor.execute("Select * from food where foodID = ?", id)
        result = []
        keys = []
        for i in cursor.description:
            keys.append(i[0])
        for val in cursor.fetchall():
            result.append(dict(zip(keys, val)))
        resp = jsonify(result)
        print(resp)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)


@food.route('/get_food/filter', methods=['GET'])
def sort_food():
    key = request.args.get('key')   
    name = request.args.get('name')

    if name is None:
        name = ''
    try:
        cursor = conn.cursor()
        if key == 'all':
            cursor.execute("select * from Food where foodName like ?", u'%' + name + '%')
        elif key == 'promo':
            cursor.execute("select * from Food where foodName like ? and foodDiscount is not null", u'%' + name + '%')
        elif key == 'price-asc':
            cursor.execute("select *, "
                           "ROUND(CAST(foodPrice AS INT) * (100 - ISNULL(FoodDiscount, 0)) / 100, 0) AS newPrice "
                           "from food "
                           "where foodName like ? "
                           "order by newPrice asc", u'%' + name + '%')
        elif key =='price-desc':
            cursor.execute("select *, "
                           "ROUND(CAST(foodPrice AS INT) * (100 - ISNULL(FoodDiscount, 0)) / 100, 0) AS newPrice "
                           "from food "
                           "where foodName like ? "
                           "order by newPrice desc", u'%' + name + '%')

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


@food.route("/get_food/add", methods=['POST'])
def add_food():
    try:
        name = request.json.get('name')
        price = request.json.get('price')
        image = request.json.get('img')
        description = request.json.get('description')
        food_type = request.json.get('type')
        discount = request.json.get('discount')

        cursor = conn.cursor()

        cursor.execute("insert into Food(FoodName, FoodPrice, FoodImage, FoodDesc, FoodType, FoodDiscount) "
                       "values(?, ?, ?, ?, ?, ?)", name, price, image, description, food_type, discount)
        conn.commit()
        resp = jsonify(
            {
                "role": 'admin',
                "actions": 'added'
            })
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)



@food.route("/get_food/<int:id>/update", methods=['PUT'])
def food_update(id):
    try:
        name = request.json.get('name')
        price = request.json.get('price')
        image = request.json.get('img')
        description = request.json.get('description')
        food_type = request.json.get('type')
        discount = request.json.get('discount')
        cursor = conn.cursor()
        data = (name, price, image, description, food_type, discount, id)
        cursor.execute("update Food set FoodName = ?, FoodPrice = ?, FoodImage = ?, "
                       "FoodDesc = ?, FoodType = ?, FoodDiscount = ?  where FoodID = ?", data)
        conn.commit()
        resp = jsonify({
                "role": 'admin',
                "id": id,
                "actions": 'update'
            })
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)

@food.route("/get_food/<int:id>/delete", methods=['DELETE'])
def food_delete(id):
    try:    
        cursor = conn.cursor()
        cursor.execute("delete Food where FoodID = ?", id)
        conn.commit()
        resp = jsonify({
                "role": 'admin',
                "id": id,
                "actions": 'delete'
            })
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)