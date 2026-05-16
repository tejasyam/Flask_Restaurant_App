from app import application
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:12345@localhost/restaurant'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(application)

class User(db.Model):
        __tablename__ = 'user'

        user_id = db.Column(db.String(100), primary_key = True)
        name = db.Column(db.String(200), unique=True)
        username = db.Column(db.String(200), unique=True)
        password = db.Column(db.String(200))
        level = db.Column(db.Integer, default=0)
        is_active = db.Column(db.Integer, default = 1)
        created_ts = db.Column(db.DateTime, default = datetime.utcnow)
        updated_ts = db.Column(db.DateTime)

        def __init__(self, user_id, name, username, password, level):
            self.user_id = user_id
            self.name = name
            self.username = username
            self.password = password
            self.level = level
            self.is_active = 1
            self.created_ts = datetime.utcnow()

class Item(db.Model):
        __tablename__ = 'item'
    
        item_id = db.Column(db.String(100), primary_key = True)
        vendor_id = db.Column(db.String(100), db.ForeignKey("user.user_id"))
        item_name = db.Column(db.String(500))
        calories_per_gm = db.Column(db.Integer)
        available_quantity = db.Column(db.Integer)
        restaurant_name = db.Column(db.String(500))
        unit_price = db.Column(db.Integer)
        is_active = db.Column(db.Integer, default = 1)
        created_ts = db.Column(db.DateTime, default = datetime.utcnow)
        updated_ts = db.Column(db.DateTime)

        def __init__(self, item_id, vendor_id, item_name, calories_per_gm, available_quantity, restaurant_name, unit_price):
            self.item_id = item_id
            self.vendor_id = vendor_id
            self.item_name = item_name
            self.calories_per_gm = calories_per_gm
            self.available_quantity = available_quantity
            self.restaurant_name=restaurant_name
            self.unit_price = unit_price
            self.is_active = 1
            self.created_ts = datetime.utcnow()

class Order(db.Model):
        __tablename__ = 'order'
        
        order_id = db.Column(db.String(100), primary_key = True)
        user_id = db.Column(db.String(100), db.ForeignKey("user.user_id"))
        total_amount = db.Column(db.Integer, default=0)
        is_placed = db.Column(db.Integer, default=0)
        is_active = db.Column(db.Integer, default = 1)
        created_ts = db.Column(db.DateTime, default = datetime.utcnow)
        updated_ts = db.Column(db.DateTime)

        def __init__(self, order_id, user_id):
            self.order_id = order_id
            self.user_id = user_id
            self.total_amount = 0
            self.is_active = 1
            self.created_ts = datetime.utcnow()

class OrderItems(db.Model):
        __tablename__ = 'order_items'
        
        id = db.Column(db.String(100), primary_key = True)
        order_id = db.Column(db.String(100), db.ForeignKey("order.order_id"))
        item_id = db.Column(db.String(100), db.ForeignKey("item.item_id"))
        quantity = db.Column(db.Integer)
        is_active = db.Column(db.Integer, default = 1)
        created_ts = db.Column(db.DateTime, default = datetime.utcnow)
        updated_ts = db.Column(db.DateTime)

        def __init__(self, id, order_id, item_id, quantity):
            self.id = id
            self.order_id = order_id
            self.item_id = item_id
            self.quantity = quantity
            self.is_active = 1
            self.created_ts = datetime.utcnow()
with application.app_context():
    db.create_all()
    db.session.commit()