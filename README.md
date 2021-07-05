![Image of stock portfolio](/static/finance.jpg)

# Finance
Finance is a web project created as an assignment for week 9 of Harvard CS50 by Rohan Muppa on the week of July 3rd 2021 (7/3/21). The application was made using Python, HTML (w/ Jinja), CSS, and Javascript using the FLask web framework. It uses the IEX API to get the stock prices in real time and a SQL database to store user and transaction information.

Once you register and log yourself in there will be 5 main sections:

* **Portfolio** is the default route that is opened up once you log in. Portfolio will show to you all the stocks that you own along with some details about it. Portfolio also provides you with your current cash balance and your combined net worth.
* **Quote** allows you to search up the current value of a stock by entering it's ticker into the search box then pressing search.
* **Buy** allows you to buy your desired stocks. Enter the stock ticker and the amount of shares you want to buy then the transaction will proceed and your information will be updated in the SQL database. An error will occur if you cannot afford that many shares or if you enter an invalid stock ticker.
* **Sell** allows you to sell any shares of a stock that you own. Select the stock then enter the number of shares you would like to sell. An error will occur if you choose to sell more shares than you currently own.
* **History** will show to you all the previous transactions that you've made. The ticker symbol; number of shares; purchase price; total amount, in US dollars, spent during that
transaction; and the time of transaction in UTC (Coordinated Universal Time) will all be displayed to you on the screen.
# Extras
* **Log out** clears all your cookies effectively logging you out, prompting you to log in (or register) again.
* **Rohan Muppa** opens up a new page once clicked giving you more information about the website and it's functionality.

# Usage
Finance can be accessed and ran either **locally**, on your own computer, or **online**, hosted by a web server.
### Online
1. To access the application online open `https://rohan-finance.herokuapp.com` in a new browser tab.
### Locally
1. First, running the application locally requires you to change directory or `cd` into your desired directory using the terminal then clone this repository with `git clone https://github.com/RohanMuppa/Finance.git` to download the repository locally.
1. After that install Python using the [Python documentation](https://docs.python.org/3/using/index.html) as an installation guide.
1. Finally, read the [Flask documentation](https://flask.palletsprojects.com/en/2.0.x/installation/#) to install and run Flask, as well as, optionally learning how it works.
