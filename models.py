from sqlalchemy import create_engine, Column, String, Float, Date, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# Define the HistoricalData model
class HistoricalData(Base):
    __tablename__ = 'historical_data'

    id = Column(Integer, primary_key=True)
    ticker = Column(String, index=True)
    date = Column(Date, index=True)
    close = Column(Float)

# Set up the database connection
engine = create_engine('sqlite:///etf_data.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
