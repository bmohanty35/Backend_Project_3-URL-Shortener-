#S-1: import Flask and required modules


import random
import string
import validators                                                            # import random module to generate random short codes, string module to get letters and digits, and validators to validate URLs


from flask import Flask, render_template, request, redirect, url_for, flash  # import Flask tools for web app, HTML rendering, form handling, redirect, to generate route URLs and flash messages


from flask_sqlalchemy import SQLAlchemy                                      # import SQLAlchemy for database ORM to connect Python with database

# ---------------- APP SETUP ---------------- #

#S-2: Initialize the Flask object
app = Flask(__name__)
app.secret_key = "secret"                                                    # secret key is used to secure session and flash messages                     


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.sqlite"              # set SQLite database file for storing URLs


app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False                         # disable modification tracking to improve performance

db = SQLAlchemy(app)                                                         # connect SQLAlchemy with Flask app

# ---------------- Database MODEL ---------------- #

# create database table structure
class ShortURL(db.Model):
    id = db.Column(db.Integer, primary_key=True)                       # create unique ID for each record
    original_url = db.Column(db.Text, nullable=False)                  # store original long URL
    short_code = db.Column(db.String(10), unique=True, nullable=False) # store short code (must be unique)

# create database tables 
with app.app_context():
    db.create_all()

# ---------------- HELPERS ---------------- #

# function to generate random short code
def generate_code(length=6):
    chars = string.ascii_letters + string.digits                      # characters allowed in short code
    return "".join(random.choice(chars) for _ in range(length))       # return random string of given length

# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/shorten", methods=["POST"])
def shorten():
    long_url = request.form.get("long_url")

    # validate URL (check if URL is empty or invalid)
    if not long_url or not validators.url(long_url):
        flash("Please enter a valid URL (with http:// or https://)")         # show error message to user
        return redirect(url_for("home"))                                     # redirect back to home page

    # generate unique short code
    code = generate_code()
    while ShortURL.query.filter_by(short_code=code).first():                 # regenerate code if already exists in database
        code = generate_code()

    # save to DB
    url = ShortURL(original_url=long_url, short_code=code)                   # create new database record
    db.session.add(url)                                                      # add record to database session
    db.session.commit()                                                      # save record permanently in database
 
    short_url = request.host_url + code                                      # create full short URL using host and code
    return render_template("home.html", short_url=short_url)                 # show short URL on home page


@app.route("/history")
def history():
    urls = ShortURL.query.all()                                              # fetch all URL records from database
    return render_template("history.html", urls=urls)                        # send URL list to history page


@app.route("/<code>")                                                        # dynamic route to redirect short URL to original URL
def redirect_url(code):
    url = ShortURL.query.filter_by(short_code=code).first()                  # find original URL using short code              
    if url:
        return redirect(url.original_url)                                    # if found, redirect to original website
    return "URL not found", 404                                              # if not found, return error message


if __name__ == "__main__":
    app.run(debug=True)
