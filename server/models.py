from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

# Restaurant Model
class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # Relationship to RestaurantPizza
    restaurant_pizzas = db.relationship('RestaurantPizza', back_populates='restaurant', cascade='all, delete-orphan')

    # Relationship to Pizza (through RestaurantPizza)
    pizzas = association_proxy('restaurant_pizzas', 'pizza')

    # Serializer rules to limit recursion depth
    serialize_rules = ('-restaurant_pizzas.restaurant', '-restaurant_pizzas.pizza')

    def __repr__(self):
        return f"<Restaurant {self.name}>"

# Pizza Model
class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # Relationship to RestaurantPizza
    restaurant_pizzas = db.relationship('RestaurantPizza', back_populates='pizza', cascade='all, delete-orphan')

    # Relationship to Restaurant (through RestaurantPizza)
    restaurants = association_proxy('restaurant_pizzas', 'restaurant')

    # Serializer rules to limit recursion depth
    serialize_rules = ('-restaurant_pizzas.pizza', '-restaurant_pizzas.restaurant')

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"

# RestaurantPizza Model
class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    # Foreign Keys
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))

    # Relationships
    pizza = db.relationship('Pizza', back_populates='restaurant_pizzas')
    restaurant = db.relationship('Restaurant', back_populates='restaurant_pizzas')

    # Serializer rules to limit recursion depth
    serialize_rules = ('-pizza.restaurant_pizzas', '-restaurant.restaurant_pizzas')

    # Validation for price
    @validates('price')
    def validate_price(self, key, value):
        if value < 1 or value > 30:
            raise ValueError("Price must be between 1 and 30.")
        return value

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"

    # Modified to_dict method to include relationships when needed
    def to_dict(self, include_relationships=False):
        # Default behavior (without relationships)
        data = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        
        if include_relationships:
            # Include related models' data if requested
            data['pizza'] = self.pizza.to_dict() if self.pizza else None
            data['restaurant'] = self.restaurant.to_dict() if self.restaurant else None
        
        return data