import yfinance as yf
from datetime import datetime
from models import HistoricalData, session

def get_historical_data(ticker, start_date, end_date):
    # Convert dates to datetime objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    # Query the database for the specified date range
    existing_data = session.query(HistoricalData).filter(
        HistoricalData.ticker == ticker,
        HistoricalData.date >= start_date,
        HistoricalData.date <= end_date
    ).all()

    # If data is found in the database, return it
    if existing_data:
        print(f"Data fetched from database for {ticker}")
        return {record.date.isoformat(): {"Close": record.close} for record in existing_data}
    
    # Fetch data from the API if not found in the database
    print(f"Fetching data from API for {ticker}")
    etf = yf.Ticker(ticker)
    history = etf.history(start=start_date, end=end_date, interval="1wk")

    # Check if the API returned data
    if history.empty:
        return None

    # Save the API data to the database
    for date, row in history.iterrows():
        session.add(HistoricalData(
            ticker=ticker,
            date=date.date(),
            close=row['Close']
        ))
    session.commit()

    # Return the fetched data
    return history[['Close']].to_dict('index')
