from app import application
from flask import jsonify, session
from app.models import *
from app import *
import uuid
from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs


class SignUpRequest(Schema):
    username = fields.Str(default='username')
    password = fields.Str(default='password')
    name = fields.Str(default='name')
    level = fields.Int(default=0)


class LoginRequest(Schema):
    username = fields.Str(default='username')
    password = fields.Str(default='password')


class AddVendorRequest(Schema):
    user_id = fields.Str(default='user_id')


class AddItemRequest(Schema):
    item_name = fields.Str(default='item_name')
    calories_per_gm = fields.Int(default=100)
    available_quantity = fields.Int(default=100)
    restaurant_name = fields.Str(default='abc hotel')
    unit_price = fields.Int(default=0)


class VendorsListResponse(Schema):
    vendors = fields.List(fields.Dict())


class ItemListResponse(Schema):
    items = fields.List(fields.Dict())


class APIResponse(Schema):
    message = fields.Str(default='Success')


class ItemsOrderList(Schema):
    items = fields.List(fields.Dict())


class PlaceOrderRequest(Schema):
    order_id = fields.Str(default='order_id')


class ListOrderResponse(Schema):
    orders = fields.List(fields.Dict())


class SignUpAPI(MethodResource, Resource):

    @doc(description="Sign Up API", tags=['SignUP API'])
    @use_kwargs(SignUpRequest, location='json')
    @marshal_with(APIResponse)
    def post(self, **kwargs):
        try:
            existing_user = User.query.filter_by(username=kwargs['username']).first()

            if existing_user:
                return APIResponse().dump(dict(message='Username already exists')), 400

            user = User(
                str(uuid.uuid4()),
                kwargs['name'],
                kwargs['username'],
                kwargs['password'],
                kwargs['level']
            )

            db.session.add(user)
            db.session.commit()

            return APIResponse().dump(dict(message='User is successfully registered')), 200

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to register User : {str(e)}')), 400


api.add_resource(SignUpAPI, '/signup')
docs.register(SignUpAPI)


class LoginAPI(MethodResource, Resource):

    @doc(description='Login API', tags=['Login API'])
    @use_kwargs(LoginRequest, location='json')
    @marshal_with(APIResponse)
    def post(self, **kwargs):
        try:
            user = User.query.filter_by(
                username=kwargs['username'],
                password=kwargs['password']
            ).first()

            if user:
                session['user_id'] = user.user_id
                return APIResponse().dump(dict(message='User is successfully logged in')), 200

            return APIResponse().dump(dict(message='User not found')), 404

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to find login User : {str(e)}')), 400


api.add_resource(LoginAPI, '/login')
docs.register(LoginAPI)


class LogoutAPI(MethodResource, Resource):

    @doc(description='Logout API', tags=['Logout API'])
    @marshal_with(APIResponse)
    def post(self, **kwargs):
        try:
            if session.get('user_id'):
                session.pop('user_id', None)
                return APIResponse().dump(dict(message='User is successfully logged out')), 200

            return APIResponse().dump(dict(message='User is not logged in')), 401

        except Exception as e:
            return APIResponse().dump(dict(message=f'Not able to logout User : {str(e)}')), 400


api.add_resource(LogoutAPI, '/logout')
docs.register(LogoutAPI)


class AddVendorAPI(MethodResource, Resource):

    @doc(description='Add Vendor API', tags=['Vendor API'])
    @use_kwargs(AddVendorRequest, location='json')
    @marshal_with(APIResponse)
    def post(self, **kwargs):
        try:
            if not session.get('user_id'):
                return APIResponse().dump(dict(message='User is not logged in')), 401

            logged_user = User.query.filter_by(user_id=session['user_id']).first()

            if logged_user.level != 2:
                return APIResponse().dump(dict(message='Logged User is not Admin')), 405

            vendor_user_id = kwargs['user_id']
            user = User.query.filter_by(user_id=vendor_user_id).first()

            if not user:
                return APIResponse().dump(dict(message='User not found')), 404

            user.level = 1
            db.session.commit()

            return APIResponse().dump(dict(message='Vendor is successfully added')), 200

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to add vendor : {str(e)}')), 400


api.add_resource(AddVendorAPI, '/add_vendor')
docs.register(AddVendorAPI)


class GetVendorsAPI(MethodResource, Resource):

    @doc(description='Get All Vendors API', tags=['Vendor API'])
    def get(self):
        try:
            if not session.get('user_id'):
                return APIResponse().dump(dict(message='User is not logged in')), 401

            vendors = User.query.filter_by(level=1).all()
            vendors_list = []

            for vendor in vendors:
                vendor_items = Item.query.filter_by(vendor_id=vendor.user_id).all()
                items_list = []

                for item in vendor_items:
                    items_list.append({
                        'item_id': item.item_id,
                        'item_name': item.item_name,
                        'calories_per_gm': item.calories_per_gm,
                        'available_quantity': item.available_quantity,
                        'restaurant_name': item.restaurant_name,
                        'unit_price': item.unit_price
                    })

                vendors_list.append({
                    'vendor_id': vendor.user_id,
                    'name': vendor.name,
                    'items': items_list
                })

            return VendorsListResponse().dump(dict(vendors=vendors_list)), 200

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to list vendors : {str(e)}')), 400


api.add_resource(GetVendorsAPI, '/list_vendors')
docs.register(GetVendorsAPI)


class AddItemAPI(MethodResource, Resource):

    @doc(description='Add Item API', tags=['Items API'])
    @use_kwargs(AddItemRequest, location='json')
    @marshal_with(APIResponse)
    def post(self, **kwargs):
        try:
            if not session.get('user_id'):
                return APIResponse().dump(dict(message='Vendor is not logged in')), 401

            user = User.query.filter_by(user_id=session['user_id']).first()

            if user.level != 1:
                return APIResponse().dump(dict(message='Logged in user is not a Vendor')), 405

            item = Item(
                str(uuid.uuid4()),
                session['user_id'],
                kwargs['item_name'],
                kwargs['calories_per_gm'],
                kwargs['available_quantity'],
                kwargs['restaurant_name'],
                kwargs['unit_price']
            )

            db.session.add(item)
            db.session.commit()

            return APIResponse().dump(dict(message='Item is successfully added')), 200

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to add item : {str(e)}')), 400


api.add_resource(AddItemAPI, '/add_item')
docs.register(AddItemAPI)


class ListItemsAPI(MethodResource, Resource):

    @doc(description='List All Items API', tags=['Items API'])
    def get(self):
        try:
            if not session.get('user_id'):
                return APIResponse().dump(dict(message='User is not logged in')), 401

            items = Item.query.all()
            items_list = []

            for item in items:
                items_list.append({
                    'item_id': item.item_id,
                    'vendor_id': item.vendor_id,
                    'item_name': item.item_name,
                    'calories_per_gm': item.calories_per_gm,
                    'available_quantity': item.available_quantity,
                    'restaurant_name': item.restaurant_name,
                    'unit_price': item.unit_price
                })

            return ItemListResponse().dump(dict(items=items_list)), 200

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to list items : {str(e)}')), 400


api.add_resource(ListItemsAPI, '/list_items')
docs.register(ListItemsAPI)


class CreateItemOrderAPI(MethodResource, Resource):

    @doc(description='Create Items Order API', tags=['Order API'])
    @use_kwargs(ItemsOrderList, location='json')
    @marshal_with(APIResponse)
    def post(self, **kwargs):
        try:
            if not session.get('user_id'):
                return APIResponse().dump(dict(message='Customer is not logged in')), 401

            user_id = session['user_id']
            user_type = User.query.filter_by(user_id=user_id).first().level

            if user_type != 0:
                return APIResponse().dump(dict(message='LoggedIn User is not a Customer')), 405

            order_id = str(uuid.uuid4())
            order = Order(order_id, user_id)

            db.session.add(order)

            for item in kwargs['items']:
                order_item = OrderItems(
                    str(uuid.uuid4()),
                    order_id,
                    item['item_id'],
                    item['quantity']
                )
                db.session.add(order_item)

            db.session.commit()

            return APIResponse().dump(dict(message='Items for the Order are successful')), 200

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to add items for ordering : {str(e)}')), 400


api.add_resource(CreateItemOrderAPI, '/create_items_order')
docs.register(CreateItemOrderAPI)


class PlaceOrderAPI(MethodResource, Resource):

    @doc(description='Place Order API', tags=['Order API'])
    @use_kwargs(PlaceOrderRequest, location='json')
    @marshal_with(APIResponse)
    def post(self, **kwargs):
        try:
            if not session.get('user_id'):
                return APIResponse().dump(dict(message='Customer is not logged in')), 401

            user_id = session['user_id']
            user = User.query.filter_by(user_id=user_id).first()

            if user.level != 0:
                return APIResponse().dump(dict(message='LoggedIn User is not a Customer')), 405

            order_id = kwargs['order_id']
            order = Order.query.filter_by(order_id=order_id).first()

            if not order:
                return APIResponse().dump(dict(message='Order not found')), 404

            order_items = OrderItems.query.filter_by(order_id=order_id).all()

            if not order_items:
                return APIResponse().dump(dict(message='No items found in order')), 404

            total_amount = 0

            for order_item in order_items:
                item = Item.query.filter_by(item_id=order_item.item_id).first()

                if not item:
                    return APIResponse().dump(dict(message='Item not found')), 404

                if item.available_quantity < order_item.quantity:
                    return APIResponse().dump(dict(message='Item quantity not available')), 400

                total_amount += item.unit_price * order_item.quantity
                item.available_quantity -= order_item.quantity

            order.total_amount = total_amount
            order.is_placed = True

            db.session.commit()

            return APIResponse().dump(dict(message='Order is successfully placed')), 200

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to place order : {str(e)}')), 400


api.add_resource(PlaceOrderAPI, '/place_order')
docs.register(PlaceOrderAPI)


class ListOrdersByCustomerAPI(MethodResource, Resource):

    @doc(description='List Orders By Customer API', tags=['Order API'])
    def get(self):
        try:
            if not session.get('user_id'):
                return APIResponse().dump(dict(message='User is not logged in')), 401

            user_id = session['user_id']
            orders = Order.query.filter_by(user_id=user_id).all()
            orders_list = []

            for order in orders:
                order_items = OrderItems.query.filter_by(order_id=order.order_id).all()
                items_list = []

                for order_item in order_items:
                    item = Item.query.filter_by(item_id=order_item.item_id).first()

                    items_list.append({
                        'item_id': order_item.item_id,
                        'item_name': item.item_name if item else None,
                        'quantity': order_item.quantity
                    })

                orders_list.append({
                    'order_id': order.order_id,
                    'user_id': order.user_id,
                    'total_amount': order.total_amount,
                    'is_placed': order.is_placed,
                    'items': items_list
                })

            return ListOrderResponse().dump(dict(orders=orders_list)), 200

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to list orders : {str(e)}')), 400


api.add_resource(ListOrdersByCustomerAPI, '/list_orders')
docs.register(ListOrdersByCustomerAPI)


class ListAllOrdersAPI(MethodResource, Resource):

    @doc(description='List All Orders API', tags=['Order API'])
    def get(self):
        try:
            if not session.get('user_id'):
                return APIResponse().dump(dict(message='User is not logged in')), 401

            user_id = session['user_id']
            user = User.query.filter_by(user_id=user_id).first()

            if user.level != 2:
                return APIResponse().dump(dict(message='Logged User is not Admin')), 405

            orders = Order.query.all()
            orders_list = []

            for order in orders:
                order_items = OrderItems.query.filter_by(order_id=order.order_id).all()
                items_list = []

                for order_item in order_items:
                    item = Item.query.filter_by(item_id=order_item.item_id).first()

                    items_list.append({
                        'item_id': order_item.item_id,
                        'item_name': item.item_name if item else None,
                        'quantity': order_item.quantity
                    })

                orders_list.append({
                    'order_id': order.order_id,
                    'user_id': order.user_id,
                    'total_amount': order.total_amount,
                    'is_placed': order.is_placed,
                    'items': items_list
                })

            return ListOrderResponse().dump(dict(orders=orders_list)), 200

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to list all orders : {str(e)}')), 400


api.add_resource(ListAllOrdersAPI, '/list_all_orders')
docs.register(ListAllOrdersAPI)