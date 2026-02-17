from flask import Flask, render_template, request, redirect, url_for
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


@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    pass
    


@app.route('/add', methods=['POST'])
def add():
    cn = False
    names = request.form.get('name')
    pizza = request.form.get('pizza')
    pizaas = Pizza.query.all()
    for pizzas in pizaas:
        print(pizzas, pizza)
        if pizza == pizzas.name:
            nid = pizzas.id
            cn = True
    
        
    
    if cn:
        user = db.session.scalar(select(User).where(User.name == names))
        print(user)
        if not user:
            new_user = User(name=names)
            db.session.add(new_user)
            db.session.commit()
            user = db.session.scalar(select(User).where(User.name == names))
        
        print(user.id, nid)
        nO = Order(user_id=user.id, pizza_id=nid)
        db.session.add(nO)
        db.session.commit()
        db.session.close()
    return redirect(url_for('index'))

@app.route('/index')
def index():
    print('hi')
    info = []
    userss = []
    pzza = []
    pizzas = Pizza.query.all()
    for pizza in pizzas:
        pzza.append((pizza.id, pizza.name, pizza.topping))
   
    users = User.query.all()
    for user in users:
        print(user)
        info.append((user.name, user.id))
        userss.append(user.name)
    


    results = User.query.join(User.orders).join(Order.pizza).add_entity(Pizza).add_entity(Order).all()
    oderings = []
    for i in results:
        oderings.append((i[0].name, i[1].topping, i[2].id))
  
   
    

    


    return render_template('index.html', info=info, results=results, oderings=oderings, userss=userss, pzza=pzza)

if __name__ == '__main__':
    app.run(debug=True)