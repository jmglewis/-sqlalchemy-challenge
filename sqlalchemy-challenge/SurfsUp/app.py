# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify, request

#################################################
# Database Setup
# Replace 'your_database_file_path' with the absolute path to your SQLite database file
database_path = 'C:/Users/Joanna/Desktop/sqlalchemy-challenge/SurfsUp/Resources/hawaii.sqlite'
engine = create_engine(f"sqlite:///{database_path}")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(autoload_with=engine)
Base.classes.keys()
# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
app = Flask (__name__)
#################################################

# Flask Routes
@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

# Flask Routes
@app.route("/api/v1.0/precipitation")
def prec():
    # Create session
    session=Session(engine)

    # Query the most recent date in the database
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]

    # Convert the recent date to a datetime object
    recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d')

    # Calculate the date one year ago from the most recent date
    one_year_ago = recent_date - dt.timedelta(days=365)

    # Query precipitation data for the last 12 months
    results = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= one_year_ago).\
        order_by(measurement.date).all()

    # Create a DataFrame and set the date as the index
    df = pd.DataFrame(results, columns=['date', 'precipitation'])
    df.set_index('date', inplace=True)

    # Sort the DataFrame by date
    df = df.sort_index()

    # Handle duplicate date entries
    df = df[~df.index.duplicated(keep='first')]

    # Convert the DataFrame to a dictionary for JSON response
    summary = df.to_dict(orient='index')

    session.close()
    return jsonify(summary)

# Flask Routes
@app.route("/api/v1.0/stations")
def get_stations():
    # Create a SQLAlchemy session
    session = Session(engine)

    # Query all stations
    stations = session.query(station.station).all()

    # Convert the list of stations to a dictionary for JSON response
    station_data = {"stations": [station[0] for station in stations]}

    # Close the SQLAlchemy session
    session.close()

    return jsonify(station_data)
# Flask Routes
@app.route("/api/v1.0/tobs")
def tob():
    """Return a JSON list of temperature observations for the previous year."""
    session = Session(engine)

    # Query for the latest date with temperature observations
    latest_date_with_data = session.query(func.max(measurement.date)).scalar()

    # Convert the latest date to a datetime object
    end_date = dt.datetime.strptime(latest_date_with_data, '%Y-%m-%d')

    # Calculate the start date as one year ago from the latest date
    start_date = end_date - dt.timedelta(days=365)

    # Query temperature data for the last 12 months for the most active station
    temperature_data = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == "USC00519281").\
        filter(measurement.date.between(start_date, end_date)).all()

    # Create a list of dictionaries for JSON response
    temperature_list = [{"date": date, "tobs": tobs} for date, tobs in temperature_data]

    # Close the session
    session.close()

    # Return the temperature data as JSON
    return jsonify(temperature_list)

from flask import Flask, jsonify, request
# ... (import other necessary modules)

# Flask app initialization and configuration

# Flask Routes
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end=None):
    """Return JSON list of min/avg/max temp between given start and end dates"""
    session = Session(engine)
    start_date = request.args.get('start', '2010-01-01')
    end_date = request.args.get('end', '2017-08-23')
    
    # Querying the database with filters based on start and end dates
    results = session.query(func.min(measurement.tobs),
                            func.max(measurement.tobs),
                            func.avg(measurement.tobs)).\
                            filter(measurement.date >= start_date).\
                            filter(measurement.date <= end_date).all()
    
    # Creating a list of dictionaries to store temperature information
    tobs_list = []
    for tmin, tmax, tavg in results:
        tobs_dict = {
            "TMIN": tmin,
            "TMAX": tmax,
            "TAVG": tavg
        }
        tobs_list.append(tobs_dict)
    
    session.close()  # Close the session after use

    return jsonify(tobs_list)

if __name__ == "__main__":
    app.run(debug=True)
#################################################
