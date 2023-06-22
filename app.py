from flask import request,abort,json,jsonify,make_response,redirect
import jwt
import datetime
import os
from models import app,Resturant,Menu,Order,User,startDb,AuthError,Admin
from functools import wraps
from werkzeug.exceptions import NotFound

"""
@TODO Run Once.
"""
# startDb()
"""
    ^
    |
    Uncomment. Access one of the endpoints either in a browser or in terminal, once. Comment it again.
"""
def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token = os.environ['TOKEN']
        if not token:
            abort(401)
        try:
            data = jwt.decode(token,app.secret_key,['HS256'])
        except Exception as e:
            abort(500)
        return f(*args,**kwargs)
    return decorated

@app.route('/login')
def verify():
    # get the authorzation header
    auth = request.authorization

    if auth:
        name  = auth.username
        password = auth.password

        #get use according to the authorization header
        user = User.query.filter(User.name == name, User.password == password).one_or_none()

        if user is not None:
            #create JWT and set it to the TOKEN varibale
            os.environ['TOKEN'] = jwt.encode({"user":name,"exp":datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},app.secret_key,"HS256")
            return  jsonify({"success":True,"message":"User verified"})
    return make_response('Could not verify',401,{'WWW-Authenticate':'Basic real="Login Required'})


@app.route('/resturants')
def get_returants():
    try:
        resturants = [r.getResturant() for r in Resturant.query.all()]
        return jsonify({"success":True,"resturants":resturants})
    except:
        abort(500)

@app.route('/resturants/<int:id>')
def get_resturant(id):
        menu = Resturant.query.filter(Resturant.id == id).one_or_none()
        if menu is None:
            abort(404)
        return jsonify({"success":True,"menu":menu.getResturant()})



@app.route('/menus')
def get_all_menus():
    try:
        menus = [m.getMenu() for m in Menu.query.all()]
    except:
        abort(500)
    return jsonify({"success":True,"menus":menus})

@app.route('/menus/<int:id>')
def get_menu(id):
        menu = Menu.query.filter(Menu.id == id).one_or_none()
        if menu is None:
            abort(404)
        else:
            return jsonify({"success":True,"menu":menu.getMenu()})  





@app.route('/order',methods=['POST'])
@token_required
def place_order():
    try:
        req = request.get_json()
        order = Order(req['user_id'],req['resturant_id'],req['menu_id'],req['items'])
        order.addOrder() 
    except:
        abort(500)
    return jsonify({"success":True,"order":order.getOrder()})    


@app.route('/complete-order',methods=['PATCH'])
def complete_order():
    id = request.get_json()['id']
    try:
        order = Order.query.filter(Order.id == id).one_or_none()
        if order is not None:
            order.completeOrder()
            return jsonify({"success":True,"message":f"Order number {id} has been fulfilled"})
        abort(404)
    except Exception as e:
        return jsonify({"message":str(e)})

@app.route('/cancel-order',methods=['POST'])
@token_required
def cancel_order():
    req = request.get_json()
    order = Order.query.filter(Order.id == req.get('id',None)).one_or_none()
    if order is None:
        abort(404)
    order.cancelOrder()
    return jsonify({"success":True,"message":"Order cancelled"})

@app.route('/history')
@token_required
def get_history():
    orders = [r.getOrder() for r in Order.query.filter(Order.cancel == True or Order.completed == True).all()]
    return jsonify({"history":orders})





"""
======================================================= A D M I N =====================================================
"""

def admin_token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token = os.environ['ADMIN_TOKEN']
        if not token:
            abort(401)
        try:
            data = jwt.decode(token,app.secret_key,['HS256'])
        except Exception as e:
            abort(500)
        return f(*args,**kwargs)
    return decorated


@app.route('/admin')
def admin_login():
    auth = request.authorization

    if auth:
        name  = auth.username
        password = auth.password

        #get use according to the authorization header
        user = Admin.query.filter(Admin.admin_id == name, Admin.password == password).one_or_none()

        if user is not None:
            #create JWT and set it to the TOKEN varibale
            os.environ['ADMIN_TOKEN'] = jwt.encode({"admin_id":name,"exp":datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},app.secret_key,"HS256")
            return  jsonify({"success":True,"message":"Admin verified"})
    return make_response('Could not verify Admin',401,{'WWW-Authenticate':'Basic real="Login Required'})

@app.route('/order-received',methods=['POST'])
@admin_token_required
def received():
    req = request.get_json()
    order_id = req.get('id',None)
    order = Order.query.filter(Order.id == order_id).one_or_none()
    if order is None:
        abort(404)
    order.confirmOrder()
    return jsonify({"success":True,"message":"Order confirmed"})

@app.route('/put-in-preparation',methods=['POST'])
@admin_token_required
def put_in_preparation():

    order = Order.query.filter(Order.id == request.get_json()['id']).one_or_none()
    if order is None:
        abort(404)
    order.put_in_Preparation()
    return jsonify({"success":True,"message":"Order is in preparation now"})

@app.route('/in-transit',methods=['POST'])
@admin_token_required
def put_order_in_transit():
    req = request.get_json()
    id = req.get('id',None)
    order = Order.query.filter(Order.id == id).one_or_none()
    if order is None:
        abort(404)
    order.outForDeliver()
    return jsonify({"success":True,"message":f"Order {id} is in transit for delivery"})

@app.route('/out-for-delivery')
@admin_token_required
def get_all_in_deliver():
    try:
        orders = [r.getOrder() for r in Order.query.filter(Order.cancel == False, Order.completed == False,Order.out_for_delivery == True).all()]
        return jsonify({"orders_in_delivery":orders,"total":len(orders)}) 
    except:
        abort(500)       
@app.route('/in-preparation')
@admin_token_required
def all_in_preparation():
    try:
        orders = [r.getOrder() for r in Order.query.filter(Order.in_preparation == True, Order.completed == False,Order.cancel == False,Order.out_for_delivery == False).all()]
        return jsonify({"orders_in_preparation":orders,"total":len(orders)})
    except:
        abort(500)


"""
view menus
place order
order fulfillment
"""




@app.errorhandler(400)
def bad_request(code):
    return jsonify({"success":False,"message":"Bad Request", 
    "error": 400,}), 400
@app.errorhandler(500)
def internal_error(code):
    return jsonify({"success":False,"message":"Internal Error", 
    "error": 500,}), 500
    
@app.errorhandler(NotFound)
def not_found(code):
    return jsonify({"success":False,"message":"Resource not found", 
    "error": 404,})

@app.errorhandler(401)
def user_not_authorized(code):
    return jsonify({"success":False,"message":"User is not authorized.", 
    "error": code,}), 401


@app.errorhandler(405)
def method_not_alloed(code):

    return jsonify({"success":False,"message":f"{request.method} is not allowed on this endpoint", 
    "error": 405,}), 405



if __name__ == "__main__":
    app.run(debug=True)