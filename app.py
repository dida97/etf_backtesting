from flask import Flask, render_template, request
import yfinance as yf 
from utils import get_historical_data
import pandas as pd

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/search', methods=['POST'])
def search():
    ticker = request.form['ticker'].upper()
    start_date = request.form.get('start_date') or "2017-01-01"
    end_date = request.form.get('end_date') or pd.Timestamp.today().strftime('%Y-%m-%d')

    # Fetch historical data using the database-backed function
    historical_prices = get_historical_data(ticker, start_date, end_date)

    if not historical_prices:
        return render_template('error.html', message=f"No data found for '{ticker}' in the selected range.")

    return render_template('results.html', ticker=ticker, historical_prices=historical_prices,
                           start_date=start_date, end_date=end_date)


if __name__ == '__main__':
    app.run(debug=True)
