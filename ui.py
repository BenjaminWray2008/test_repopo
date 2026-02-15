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

class User(db.Model):




@app.route('/')
def index():
    pizzas = Pizza.query.all()
    for pizza in pizzas:
        print(pizza.name, pizza.id)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
