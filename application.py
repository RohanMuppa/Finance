import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("postgresql://dbkyqgsfhzvxtx:9969b032df90b45478ccfabf07b5ba02e42496637ed533ecb1438c64d06477f4@ec2-34-193-112-164.compute-1.amazonaws.com:5432/d87v2eo9ci6v2g")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/rohanmuppa")
@login_required
def rohanmuppa():
    """Send user information about website and it's creator"""
    return render_template("rohanmuppa.html")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show portfolio of stocks"""

    # Queries database for purchase history
    holdings = db.execute("SELECT symbol, SUM(shares) FROM transactions GROUP BY symbol HAVING id = ?",
                          session["user_id"])

    # Queries database for user cash balance
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]

    # Adds cash and stock to come to come to grand_total
    grand_total = cash

    # Iterate over the holdings
    for stock in holdings:
        symbol = stock["symbol"]
        shares = stock["SUM(shares)"]
        name = lookup(symbol)["name"]
        price = lookup(symbol)["price"]
        stock["name"] = name
        stock["price"] = usd(price)
        stock["total"] = price*shares
        grand_total += stock["total"]

    return render_template("index.html", holdings=holdings, cash=usd(cash), grand_total=usd(grand_total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Makes sure symbol is valid
        if lookup(symbol) == None:
            return apology("invalid symbol")

        price = lookup(symbol)["price"]
        name = lookup(symbol)["name"]

        # Queries database to check how much cash the user has
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]

        total = float(price) * int(shares)

        # Makes sure user has enough cash to buy the stocks
        if total > cash:
            return apology("insufficient funds")

        # Completes transaction
        cash -= total

        # Updates database with new information
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, session["user_id"])

        db.execute("INSERT INTO transactions (id, name, symbol, shares, price, total, date) VALUES (:id, :name, :symbol, :shares, :price, :total, :date)",
                   id=session["user_id"], name=name, symbol=symbol, shares=shares, price=price, total=total, date=datetime.now())

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("buy.html")


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    """Show history of transactions"""
    transactions = db.execute("SELECT symbol,shares,date FROM transactions;")
    for transaction in transactions:
        transaction["price"] = lookup(transaction["symbol"])["price"]
    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("quote.html")

    # User reached route via POST (as by submitting a form via POST)

    # Looks up stock information
    retrieve = lookup(request.form.get("symbol"))
    if retrieve == None:
        return apology("invalid symbol")

    # Send data to HTML page to show the stock information to the user
    return render_template("quoted.html", name=retrieve["name"], symbol=retrieve["symbol"], price=retrieve["price"])


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # variables for form submisssions
        name = request.form.get("username")
        hash_pass = generate_password_hash(request.form.get("password"))
        confirmation = request.form.get("confirmation")

        # Checks if user submitted correct password both times
        if not check_password_hash(hash_pass, confirmation):
            return apology("password must match password confirmation", 403)

        # Trys to insert the new user data
        try:
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                      {"username": name, "hash": hash_pass})
        # If insert fails it outputs "username has already been taken"
        except:
            return apology("username has already been taken", 403)

        # Redirect user to login page
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # User reached route via GET (as by clicking a link or via redirect)
    symbols = []
    symbols_query = db.execute("SELECT DISTINCT(symbol) FROM transactions WHERE id = ?;", session["user_id"])

    # Loops through symbols to list on drop down
    for symbol in symbols_query:
        symbols.append(symbol["symbol"])

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        symbol = request.form.get("symbol")
        sell_shares = int(request.form.get("shares"))
        price = lookup(symbol)["price"]
        total = price * sell_shares
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]

        # Amount of shares available to sell
        maximum = db.execute("SELECT SUM(shares) FROM transactions WHERE symbol = ? AND id = ?;",
                             symbol, session["user_id"])[0]["SUM(shares)"]

        # User doesn't have enough shares of symbol to complete the transaction
        if sell_shares > maximum:
            return apology("You do not have enough shares")

        name = lookup(symbol)["name"]

        # Update table
        db.execute("INSERT INTO transactions (id,name,symbol,shares,price,total,date) VALUES (:id,:name,:symbol,:shares,:price,:total,:date);",
                   id=session["user_id"], name=name, symbol=symbol, shares=sell_shares*-1, price=price, total=total*-1, date=datetime.now())

        # Update cash balance and add it to table
        cash += total
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, session["user_id"])

        # Redirect to index
        return redirect("/")

    # Renders sell.html template
    return render_template("sell.html", symbols=symbols)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    app.run()
