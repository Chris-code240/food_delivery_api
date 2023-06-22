from flask import request,abort,json,jsonify,make_response,redirect
import jwt
import datetime
import os
from models import app,Resturant,Menu,Order,User,startDb,AuthError
from functools import wraps

"""
@TODO Run Once.
"""
# startDb()

def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token = os.environ['TOKEN']
        if not token:
            abort(401)
        try:
            data = jwt.decode(token,app.secret_key,['HS256'])
        except Exception as e:
            print(e)
            abort(500)
        return f(*args,**kwargs)
    return decorated




    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get('Authorization', None)
    if auth == None:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split(' ')
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)
    else:
        token = parts[1]
        return token

@app.route('/menus')
def get_all_menus():
    try:
        menus = [m.getMenu() for m in Menu.query.all()]
    except:
        abort(500)
    return jsonify({"success":True,"menus":menus})






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




@app.route('/login')
def verify():
    auth = request.authorization
    if auth:
        name  = auth.username
        password = auth.password
        user = User.query.filter(User.name == name, User.password == password).one_or_none()
        if user is not None:
            os.environ['TOKEN'] = jwt.encode({"user":name,"exp":datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},app.secret_key,"HS256")
            return  jsonify({"success":True,"token":os.environ.get('TOKEN')})
    return make_response('Could not verify',401,{'WWW-Authenticate':'Basic real="Login Required'})

"""
view menus
place order
order fulfillment
"""




@app.errorhandler(400)
def internal_error(code):
    return jsonify({"success":False,"message":"Bad Request", 
    "error": code,}), 400
@app.errorhandler(500)
def internal_error(code):
    return jsonify({"success":False,"message":"Internal Erro", 
    "error": code,}), 500
    
@app.errorhandler(404)
def not_found(code):
    return jsonify({"success":False,"message":"Resource not found", 
    "error": code,}), 404

@app.errorhandler(401)
def user_not_authorized(code):
    return jsonify({"success":False,"message":"User is not authorized.", 
    "error": code,}), 401


@app.errorhandler(405)
def method_not_alloed(code):

    return jsonify({"success":False,"message":f"{request.method} is not allowed on this endpoint", 
    "error": code,}), 405



if __name__ == "__main__":
    app.run(debug=True)