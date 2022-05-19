from application import db, login_manager
from sqlalchemy.ext.associationproxy import association_proxy
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def user_loader(user_id):
    return(User.query.get(int(user_id)))


class UserProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.id'))
    product_id = db.Column(db.ForeignKey('product.id'))
    price_cutoff = db.Column(db.Numeric(10, 2, 2), nullable=False)
    last_updated = db.Column(
        db.DateTime, nullable=False)
    next_notification = db.Column(db.String(20), server_default="primary")
    user = db.relationship('User', backref='products')
    product = db.relationship('Product', backref='users')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    user_preferences = db.relationship(
        'UserPreferences', backref="user", uselist=False)

    def __repr__(self):
        return self.username


class UserPreferences(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    all_notifications_disabled = db.Column(
        db.Boolean, default=False, nullable=False)
    reminders_disabled = db.Column(
        db.Boolean, default=True, nullable=True)
    reminder_freq = db.Column(db.Integer, default=6, nullable=False)
    

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    price = db.Column(db.String(20), nullable=False)
    url = db.Column(db.String(500), unique=True, nullable=False)
    is_available = db.Column(db.Boolean)
    image_file = db.Column(db.String(20), nullable=False,
                           server_default='unavailable.png')


# dummy data for command line testing
def dummy_data():
    u = User(username='testuser', email='testemail', password='testpassword')
    p = Product(name='product', price=20.2, url='https://www.example.com/')
    a = UserProduct(price_cutoff=15)
    a.product = p
    u.products.append(a)
    db.session.add(u)
    db.session.add(p)
    db.session.add(a)
    db.session.commit()

# class Test(db.Model):
#     id = db.Column(db.Integer, primary_key=True)


# For use on command line for setting up the database.
# root directory -> from application.models import init_db()
def init_db():
    db.drop_all()
    db.create_all()
