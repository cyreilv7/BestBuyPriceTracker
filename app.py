from flask import Flask, render_template, redirect, url_for, flash, request
from forms import ProductInfoForm, RegistrationForm

app = Flask(__name__)

app.config['SECRET_KEY'] = '45af1ff116fa160b425e2d03204afef4'

@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def index():
    form = ProductInfoForm()
    if form.validate_on_submit():
        flash('Product is now being tracked!', 'success')

    return render_template("index.html", form=form)

if __name__ == "__main__":
  app.run(debug=True,host='0.0.0.0', port=8080)


