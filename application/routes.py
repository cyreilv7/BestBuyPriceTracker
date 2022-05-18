from application import app, db, bcrypt
from application.models import User, Product, UserPreferences, UserProduct
from application.forms import AccountPreferencesForm, ProductInfoForm, RegistrationForm, LoginForm, NewPriceCutoffForm
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from application.helpers import *
from application.bbwrapper.ProductInfo import ProductInfo
from datetime import datetime


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET' 'POST'])
@login_required
def index():
    form = ProductInfoForm()
    if form.validate_on_submit():
        product = Product.query.filter_by(url=form.url.data).first()
        association = UserProduct.query.filter_by(
            user=current_user, product=product).first()
        if product:
            if association: 
                flash('You are already tracking this item.', 'danger')
                return render_template('index.html', form=form)
        # TODO: Attempt to scrape product info. If fail, flash "There was an error tracking this product."
        else:
            product = Product(name='TestName', price=10.2, url=form.url.data)
            db.session.add(product)
        a = UserProduct(price_cutoff=int(form.price_cutoff.data))
        a.product = product
        with db.session.no_autoflush:
            # current_user.products.append(a)
            a.user = current_user
        db.session.add(a)
        db.session.commit()
        flash('Item is succesfully being tracked!', 'success')
    return render_template('index.html', form=form)

@app.route('/tracked', defaults={'product_id': None}, methods=['GET', 'POST'])
@app.route('/tracked/<int:product_id>', methods=['GET', 'POST'])
@login_required
def tracked(product_id):
    form = NewPriceCutoffForm()
    # Fetch all products tracked by the user
    products = db.session.query(Product). \
        join(UserProduct). \
        filter(UserProduct.user_id == current_user.id).all()
    # Create list of file paths to each product's image
    product_image_files = [
        url_for('static', filename=f'product_images/{f.image_file}') for f in products]
    product_attributes = zip(products, product_image_files)
    if form.validate_on_submit():
        product = Product.query.get(product_id)
        association = UserProduct.query.filter_by(user=current_user, product=product).first()
        association.price_cutoff = int(form.price_cutoff.data)
        db.session.commit()
        flash('Price cutoff succesfully updated.', 'success')
    return render_template('tracked.html', products=products, product_attributes=product_attributes, form=form)


@app.route('/stop_tracking/<int:product_id>', methods=['GET', 'POST'])
@login_required
def stop_tracking(product_id):
    # Check if product id exists or if product belongs to user
    product = Product.query.get_or_404(product_id)
    if UserProduct.query.filter_by(product=product).first().user != current_user:
        abort(403)

    # Check if the product (whose id is a query string) is being tracked by the user
    association = UserProduct.query.filter_by(user=current_user, product=product).first()
    if not association:
        return redirect(url_for('index'))
    else:
        db.session.delete(association)
        db.session.commit()
    return redirect(url_for('tracked'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if form.validate_on_submit():
        # Insert user account info into the database
        username = form.username.data
        email = form.email.data
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('You are now able to login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # Check if username matches password
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            # Parse the query string and go to that route
            next_page = request.args.get('next')
            if next_page:
                flash('Login was successful!', 'success')
                return redirect(next_page)
            else:
                flash('Login was successful!', 'success')
                return redirect(url_for('index'))

        else:
            flash('Login unsuccessful. Please check username or password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash("You've been logged out successfully!", 'success')
    return redirect(url_for('index'))


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    user = User.query.filter_by(id=current_user.id).first()
    user_prefs = UserPreferences.query.filter_by(user_id=current_user.id).first()
    form = AccountPreferencesForm()
    if form.validate_on_submit():
        if not form.disable_notifications.data:
            user_prefs.all_notifications_disabled = False
        else:
            user_prefs.all_notifications_disabled = True
        if not form.receive_reminders.data:
            user_prefs.reminders_disabled = True
        else:
            user_prefs.reminders_disabled = False
            user_prefs.reminder_freq = form.reminder_frequency.data
        
        if form.email.data != "":
            user.email = form.email.data
        if form.password.data != "":
            user.password = form.password.data
        db.session.commit()
        flash("Your account settings have been updated.", 'success')
    
    return render_template('account.html', title='Account', form=form, user=user, user_prefs=user_prefs)

@app.teardown_request
def teardown_request(exception):
    if exception:
        db.session.rollback()
    db.session.remove()

