from flask import Flask, render_template, redirect, url_for, flash, request
from forms import ProductInfoForm, RegistrationForm, LoginForm

app = Flask(__name__)

app.config['SECRET_KEY'] = '45af1ff116fa160b425e2d03204afef4'

@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def index():
    form = ProductInfoForm()
    if form.validate_on_submit():
        flash('Product is now being tracked!', 'success')
    return render_template("index.html", form=form)

@app.route("/register", methods= ['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash('Account has been created!', 'success')
    return render_template("register.html", form=form)

@app.route("/login", methods= ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login successful', 'success')
        return redirect("/")    
    return render_template("login.html", form=form)

if __name__ == "__main__":
  app.run(debug=True,host='0.0.0.0', port=8080)


