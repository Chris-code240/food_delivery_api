from flask import Flask,jsonify,json,abort
from flask_sqlalchemy import SQLAlchemy
import os
import flask_cors

app = Flask(__name__)
app.config.from_object('config')
app.secret_key = os.environ['SECRETE_KEY']
flask_cors.CORS(app)

db = SQLAlchemy(app)

def startDb():
    db.drop_all()
    db.create_all()

    res = Resturant("Resturant 1")
    res.addResturant()
    menu = Menu(1)
    menu.addMenu()

    for item in ['fufuo','banku','rice ball']:
        menu.addItem(item)

    user = User('Chris','mypassword')
    user.addUser()

    order = Order(1,1,1,['fufuo','rice ball'])
    order.addOrder()

    admin = Admin('ADMIN0101','ADMIN_password')
    admin.addAdmin()


class Resturant(db.Model):
    __tablename__ = "Resturant"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(),nullable=False)

    def __init__(self,name) -> None:
        self.name = name
    
    def addResturant(self):
        db.session.add(self)
        db.session.commit()
    
    def getResturant(self):
        try:
            menus = [m.getMenu() for m in Menu.query.filter(Menu.returant_id == self.id).all()]
            orders = [order.getOrder() for order in Order.query.filter(Order.resturant_id == self.id).all()]
        except:
            abort(500)
        return {"success":True,"id":self.id,"name":self.name,"menus":menus, "orders":orders}

class Menu(db.Model):
    __tablename__ = "Menu"
    id = db.Column(db.Integer,primary_key=True)
    returant_id = db.Column(db.Integer,db.ForeignKey('Resturant.id'), nullable=False)
    
    items = db.Column(db.String())

    def __init__(self,resturant_id) -> None:
        self.returant_id = resturant_id
        self.items = "[]"
        
    def addMenu(self):
        db.session.add(self)
        db.session.commit()


    def getMenu(self):
        orders = Order.query.filter(Order.menu_id == self.id).all()
        return {"id":self.id,"resturant_id":self.returant_id,"items":json.loads(self.items)}
    
    def addItem(self,item):
        items = json.loads(self.items)
        items.append(item)
        self.items = json.dumps(items)
        db.session.commit()

class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(),nullable=False)
    password = db.Column(db.String(),nullable=False)
    def __init__(self,name,password) -> None:
        self.name = name
        self.password = password
    
    def addUser(self):
        db.session.add(self)
        db.session.commit()
    
    def getUser(self):
        orders = [order.getOrder() for order in Order.query.filter(Order.user_id == self.id).all()]
        return {"id":self.id,"name":self.name,"orders":orders}
    
    def getUser(self):
        return {"id":self.id,"name":self.name}
        
class Order(db.Model):
    __tablename__ = "Order"
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('User.id'),nullable=False)
    resturant_id = db.Column(db.Integer(),db.ForeignKey('Resturant.id'))
    menu_id = db.Column(db.Integer,db.ForeignKey('Order.id'))
    items = db.Column(db.String(),nullable=False,default="[]")
    order_received = db.Column(db.Boolean,default=False)
    in_preparation = db.Column(db.Boolean,default=False)
    out_for_delivery = db.Column(db.Boolean,default=False)
    completed = db.Column(db.Boolean,default=False)
    cancel =  db.Column(db.Boolean,default=False) 

    def __init__(self,user_id,resturant_id,menu_id,items) -> None:
        self.user_id = user_id
        self.resturant_id = resturant_id
        self.menu_id = menu_id
        self.items = json.dumps(items)
        
    def addOrder(self):
        db.session.add(self)
        db.session.commit()

    def completeOrder(self):
        self.completed = True
        db.session.commit()
    
    def confirmOrder(self):
        self.confirmOrder = True
        db.session.commit()
    
    def outForDeliver(self):
        self.out_for_delivery = True
        db.session.commit()
    
    def put_in_Preparation(self):
        self.in_preparation = True
        db.session.commit()
    def cancelOrder(self):
        self.cancel = True
        db.session.commit()
    
    def addItem(self,item):
        items = json.loads(self.items)
        items.append(item)
        self.items = json.dumps(items)
        db.session.commit()

    def getOrder(self):
        return {"id":self.id,"resturant_id":self.resturant_id,"user_id":self.user_id,"order_received":self.order_received,"in_preparation":self.in_preparation,"out_for_delivery":self.out_for_delivery,"cancelled": self.cancel,
      "completed": self.completed,"items":json.loads(self.items)}

class Admin(db.Model):
    id = db.Column(db.Integer(),primary_key=True)
    admin_id = db.Column(db.String(),nullable=False,unique=True)
    password = db.Column(db.String(),nullable=False)

    def __init__(self,id,password):
        self.admin_id = id
        self.password = password
    
    def addAdmin(self):
        db.session.add(self)
        db.session.commit()

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

    





