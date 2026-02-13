from flask import Flask, render_template
from sqlalchemy import create_engine, Column, Integer, String, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker, Session
app = Flask(__name__)
engine = create_engine("sqlite:///database.db", echo=True)
base = declarative_base()

metadata = MetaData()
metadata.reflect(bind=engine)
print(metadata.tables.keys())
pizzanames = []

class pizza(base):
    __table__ = metadata.tables['pizza']


@app.route('/')
def index():
    with Session(engine) as session:
        pizzas = session.query(pizza).all()
        for i in pizzas:
            pizzanames.append(i.name)
    return render_template('index.html', pizzanames = pizzanames)


if __name__ == '__main__':
    app.run(debug=True)
