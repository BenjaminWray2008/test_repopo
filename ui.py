from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    abort,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, ForeignKey, select
from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column, Mapped
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.secret_key = "dev-secret-for-local"  # change for production
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
    name = db.Column(db.String, unique=True)
    password_hash = db.Column(db.String, nullable=True)
    is_owner = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

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
    order = db.session.get(Order, id)
    if not order:
        flash('Order not found')
        return redirect(url_for('index'))

    # allow owner or the user who created the order
    if session.get('is_owner') or session.get('user_id') == order.user_id:
        db.session.delete(order)
        db.session.commit()
        flash('Order deleted')
        return redirect(url_for('index'))
    else:
        abort(403)
    


@app.route('/add', methods=['POST'])
def add():
    pizza_name = request.form.get('pizza')

    pizza = Pizza.query.filter_by(name=pizza_name).first()
    if not pizza:
        flash('Pizza type not found')
        return redirect(url_for('index'))

    # prefer logged-in user
    if session.get('user_id'):
        user = db.session.get(User, session['user_id'])
    else:
        name = request.form.get('name')
        user = User.query.filter_by(name=name).first()
        if not user:
            user = User(name=name)
            db.session.add(user)
            db.session.commit()

    nO = Order(user_id=user.id, pizza_id=pizza.id)
    db.session.add(nO)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/index')
def index():
    print('hi')
    info = []
    userss = []
    # Make pizzas a simple list of names (not tuples) so templates render cleanly
    pzza = [pizza.name for pizza in Pizza.query.all()]
   
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        user = User.query.filter_by(name=name).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.name
            session['is_owner'] = bool(user.is_owner)
            flash('Logged in')
            return redirect(url_for('index'))
        flash('Invalid credentials')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out')
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        if User.query.filter_by(name=name).first():
            flash('Username already taken')
            return redirect(url_for('register'))
        user = User(name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registered — you can now log in')
        return redirect(url_for('login'))
    return render_template('register.html')


def seed_data():
    """Clear DB and create realistic sample data including an owner."""
    db.drop_all()
    db.create_all()

    # sample pizzas
    pizzas = [
        ('Margherita', 'tomato, mozzarella, basil'),
        ('Pepperoni', 'pepperoni, tomato, mozzarella'),
        ('Hawaiian', 'ham, pineapple, cheese'),
        ('Veggie Delight', 'peppers, onions, mushrooms, olives'),
    ]
    for name, topping in pizzas:
        db.session.add(Pizza(name=name, topping=topping))

    # sample users
    alice = User(name='alice')
    alice.set_password('alicepass')
    bob = User(name='bob')
    bob.set_password('bobpass')
    owner = User(name='owner')
    owner.set_password('ownerpass')
    owner.is_owner = True

    db.session.add_all([alice, bob, owner])
    db.session.commit()

    # sample orders (alice ordered Margherita, bob Pepperoni)
    mar = Pizza.query.filter_by(name='Margherita').first()
    pep = Pizza.query.filter_by(name='Pepperoni').first()
    db.session.add(Order(user_id=alice.id, pizza_id=mar.id))
    db.session.add(Order(user_id=bob.id, pizza_id=pep.id))
    db.session.commit()


@app.route('/owner')
def owner_dashboard():
    if not session.get('is_owner'):
        abort(403)
    return render_template('owner.html')


@app.route('/reset-data', methods=['POST'])
def reset_data():
    if not session.get('is_owner'):
        abort(403)
    seed_data()
    flash('Database reset with sample data')
    return redirect(url_for('owner_dashboard'))


@app.route('/')
def home():
    """Simple home/landing page."""
    return render_template('home.html')

if __name__ == '__main__':
    # Ensure DB exists and has sample data on first run
    with app.app_context():
        # Force recreate schema and seed realistic sample data on startup
        seed_data()

    app.run(debug=True)