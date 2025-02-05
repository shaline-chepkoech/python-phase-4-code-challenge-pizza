from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

# Route to list all restaurants
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict(only=("id", "name", "address")) for restaurant in restaurants])

# Route to get a specific restaurant by id
@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        return jsonify(restaurant.to_dict(only=("id", "name", "address", "restaurant_pizzas")))
    else:
        return jsonify({"error": "Restaurant not found"}), 404

# Route to delete a restaurant by id
@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    else:
        return jsonify({"error": "Restaurant not found"}), 404

# Route to list all pizzas
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict(only=("id", "name", "ingredients")) for pizza in pizzas])

# Route to create a new RestaurantPizza
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()

    # Validate the data
    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    if not pizza_id or not restaurant_id or price is None:
        return jsonify({"errors": ["Missing required fields"]}), 400

    if price < 1 or price > 30:
        return jsonify({"errors": ["validation errors"]}), 400  # Updated error message

    # Create a new RestaurantPizza object
    restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)

    try:
        db.session.add(restaurant_pizza)
        db.session.commit()

        # Fetch the pizza and restaurant data to include in the response
        pizza = Pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)

        # Return the created RestaurantPizza with pizza and restaurant details
        response = restaurant_pizza.to_dict()  # Add basic fields
        response['pizza'] = pizza.to_dict(only=("id", "name", "ingredients"))
        response['restaurant'] = restaurant.to_dict(only=("id", "name", "address"))

        return jsonify(response), 201

    except ValueError as e:
        return jsonify({"errors": ["validation errors"]}), 400  # Updated error message

# Root route
@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

if __name__ == "__main__":
    app.run(port=5555, debug=True)