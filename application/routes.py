from application import app, db, bcrypt
from application.models import User, Product, UserProduct
from application.forms import ProductInfoForm, RegistrationForm, LoginForm
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, current_user, logout_user, login_required


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET' 'POST'])
@login_required
def index():
    form = ProductInfoForm()
    if form.validate_on_submit():
        product = Product.query.filter_by(url=form.url.data).first()
        relationship = UserProduct.query.filter_by(
            user=current_user, product=product).first()
        if product:
            if relationship: 
                flash('You are already tracking this item', 'danger')
                return render_template('index.html', form=form)
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


@app.route('/currently_tracked', methods=['GET', 'POST'])
@login_required
def tracked():
    # Fetch all products tracked by the user
    products = db.session.query(Product). \
        join(UserProduct). \
        filter(UserProduct.user_id == current_user.id).all()
    # Create list of file paths to each product's image
    product_image_files = [
        url_for('static', filename=f'product_images/{f.image_file}') for f in products]
    product_attributes = zip(products, product_image_files)
    return render_template('tracked.html', products=products, product_attributes=product_attributes)

@app.route('/stop_tracking<int:product_id>', methods=['GET', 'POST'])
@login_required
def stop_tracking(product_id):
    product = Product.query.get(product_id)
    relationship = UserProduct.query.filter_by(user=current_user, product=product).first()
    if not relationship:
        return redirect(url_for('index'))
    else:
        db.session.delete(relationship)
        db.session.commit()
    return redirect(url_for('tracked'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if form.validate_on_submit():
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
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            # TODO: Figure out what this returns
            next_page = request.args.get('next')
            if next_page:
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
