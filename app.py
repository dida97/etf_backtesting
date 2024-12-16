from flask import Flask, render_template, request
import yfinance as yf 

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/search', methods=['POST'])
def search(): 
    ticker = request.form['ticker']
    try:
        etf = yf.Ticker(ticker)
        info = etf.info
        if not info or "longName" not in info:
            return render_template('error.html', message=f"No data found for ticker '{ticker}'. Please try again.")

        # Extract relevant data
        etf_name = info.get("longName", "N/A")

        # Get historical data (last 5 days)
        history = etf.history(period="5d")

        if history.empty:
            return render_template('error.html', message=f"No historical data available for '{ticker}'.")


        historical_prices = history[['Close']].to_dict('index')
    
        return render_template('results.html', ticker=ticker, etf_name=etf_name, historical_prices=historical_prices)
    except Exception as e: 
        return f"An error occurred: {str(e)}" 


if __name__ == '__main__':
    app.run(debug=True)
