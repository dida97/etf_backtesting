import yfinance as yf
from datetime import datetime, timedelta
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

    # Extract existing dates from the database
    existing_dates = {record.date for record in existing_data}

    # Check if the entire range is already in the database 
    # Use weeks because we are requesting weekly data
    total_days = int((end_date - start_date).days/7)
    full_date_range = set(start_date + timedelta(weeks=i)
                          for i in range((total_days)))
    missing_dates = full_date_range - existing_dates

    if not missing_dates:
        # All data is present in the database
        print(f"Data fetched from database for {ticker}")
        return {record.date.isoformat(): {"Close": record.close} for record in existing_data}


    # If data is missing, determine the missing range
    # XXX This will still have the drawback that if there is data missing both 
    # from the beginning and the end of the interval, the data is not asked dynamically
    # but for the whole date range
    missing_start = min(missing_dates)
    missing_end = max(missing_dates)

    print(f"Fetching missing data from API for {ticker} from {missing_start} to {missing_end}")

    # Fetch missing data from the API
    etf = yf.Ticker(ticker)
    new_history = etf.history(start=missing_start, end=missing_end + timedelta(days=1), interval="1wk")

    # Check if the API returned data
    if new_history.empty:
        print(f"No new data available for {ticker} from {missing_start} to {missing_end}")
        if existing_data: # If DB contains data, it is returned 
            return {record.date.isoformat(): {"Close": record.close} for record in existing_data}
        return None

    # Save the new data to the database
    for date, row in new_history.iterrows():
        date_obj = date.date()
        if date_obj not in existing_dates:  # Avoid duplicates
            session.add(HistoricalData(
                ticker=ticker,
                date=date_obj,
                close=row['Close']
            ))
    session.commit()

    # Combine existing and new data
    all_data = {record.date.isoformat(): {"Close": record.close} for record in existing_data}
    for date, row in new_history.iterrows():
        all_data[date.date().isoformat()] = {"Close": row['Close']}

    return all_data
