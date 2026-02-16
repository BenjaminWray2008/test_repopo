from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, ForeignKey, select
from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column, Mapped

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)


class Pizza(db.Model):
    __tablename__ = 'pizza'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    topping = db.Column(db.String)

    orders = relationship("Order", back_populates="pizza")


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    orders = relationship("Order", back_populates="user")

class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizza.id'))

    user = relationship("User", back_populates="orders")
    pizza = relationship("Pizza", back_populates="orders")




@app.route('/')
def index():
    info = []

    pizzas = Pizza.query.all()
    for pizza in pizzas:
        info.append((pizza.name, pizza.id, pizza.topping))
    users = User.query.all()
    for user in users:
        info.append((user.name, user.id))
    orders = Order.query.all()
    for order in orders:
        info.append((order.pizza_id, order.id, order.user_id))


    results = User.query.join(User.orders).join(Order.pizza).add_entity(Pizza).all()
    oderings = []
    for i in results:
        oderings.append((i[0].name, i[1].topping))

    


    return render_template('index.html', info=info, results=results, oderings=oderings)






if __name__ == '__main__':
    app.run(debug=True)
