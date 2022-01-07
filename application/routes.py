from application import app, db, bcrypt, login_manager
from application.models import User, Product, UserProduct
from application.forms import ProductInfoForm, RegistrationForm, LoginForm
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET' 'POST'])
# TODO: Consider adding a login required constraint
def index():
    form = ProductInfoForm()
    if form.validate_on_submit():
        pass
    return render_template('index.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('You are now able to login!', 'success')
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
            next_page = request.args.get('next') # TODO: Figure out what this returns
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


@app.route('/currently_tracked', methods=['GET', 'POST'])
@login_required
def tracked():
    return render_template('tracked.html')





