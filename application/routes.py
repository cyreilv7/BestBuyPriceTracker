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
        # Check for existing association between user and product
        product = Product.query.filter_by(url=form.url.data).first() # TODO: filter by sku might be more reliable
        asso = UserProduct.query.filter_by(
            user=current_user, product=product).first()
        if product:
            if asso:
                flash('You are already tracking this item.', 'danger')
                return render_template('index.html', form=form)
        else:
            # Get product info from BestBuy API
            product_object = ProductInfo(url=form.url.data)
            product_object.set_primary_info()
            product_object.save_product_image()

            product = Product(
                sku=product_object.sku,
                name=product_object.name,
                price=product_object.price,
                is_available=product_object.is_available,
                url=form.url.data,
                image_file=product_object.image_filename,
            )
            db.session.add(product)
        
        new_asso = UserProduct(last_updated=datetime.now(), price_cutoff=round(
            float(form.price_cutoff.data), 2))
        new_asso.product = product
        with db.session.no_autoflush:
            # current_user.products.append(a)
            new_asso.user = current_user
        db.session.add(new_asso)
        db.session.commit()
        flash('Item is succesfully being tracked!', 'success')
    return render_template('index.html', form=form)


@app.route('/tracked', methods=['GET', 'POST'])
@login_required
def tracked():
    # Get list of product objects
    products = db.session.query(Product). \
        join(UserProduct). \
        filter(UserProduct.user_id == current_user.id).all()

    # List of association objects between user and product
    associations = UserProduct.query.filter_by(user=current_user).all()

    # List of file paths to each product's image
    product_image_files = [url_for('static',
                                   filename=f'product_images/{product.image_file}') for product in products]

    last_updated = []
    now = datetime.now()
    for product in associations:
        str = ""
        hours_elapsed = get_hours_elapsed(product.last_updated, now)
        if hours_elapsed >= 1:
            if (hours_elapsed == 1):
                str = f"{hours_elapsed} hour"
            else:
                str = f"{hours_elapsed} hours"
        else:
            mins_elapsed = get_mins_elapsed(product.last_updated, now)
            if mins_elapsed == 1:
                str = f"{mins_elapsed} minute"
            else:
                str = f"{mins_elapsed} minutes"
        last_updated.append(str)

    product_attributes = zip(
        products, product_image_files, associations, last_updated)

    if request.method == 'POST':
        price_cutoffs = request.form.getlist('price-cutoff')
        print(price_cutoffs)
        for asso, price_cutoff in zip(associations, price_cutoffs):
            # asso = UserProduct.query.filter_by(user=current_user,
            #                                 product=product).first()
            asso.price_cutoff = round(float(price_cutoff), 2)
        db.session.commit()
        flash('Price cutoffs successfully updated.', 'success')
    return render_template('tracked.html', products=products,
                           product_attributes=product_attributes)


@app.route('/stop_tracking', methods=['GET', 'POST'])
@login_required
def stop_tracking():
    if request.method == 'POST':
        product_id = int(request.form.get("product_id"))
        product = Product.query.get(product_id)

        asso = UserProduct.query.filter_by(
            user=current_user, product=product).first()
        if not asso:
            return redirect(url_for('index'))
        else:
            db.session.delete(asso)
            db.session.commit()

    return redirect(url_for('tracked'))


@app.route('/stop_tracking_all', methods=['GET', 'POST'])
@login_required
def stop_tracking_all():
    if request.method == 'POST':
        associations = UserProduct.query.filter_by(user=current_user).all()
        for asso in associations:
            db.session.delete(asso)
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

