# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import func, create_engine, MetaData
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt

#################################################
# Database Setup
engine = create_engine("sqlite:///hawaii.sqlite")

#################################################

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
app = Flask(__name__)
#################################################

#################################################
# Flask Routes
#landing page
@app.route("/")
def home():
    #homepage - List all availabale routes.
    return (
        f"Welcome to Climate App API!<br/>"
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )
#Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date 12 months ago from most recent date of the data
    a_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= a_year_ago).all()

    #close sussion
    session.close()

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

#station route
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results = session.query(Station.station).all()

    #close session
    session.close()

    # Convert the query results to a list
    station_list = [station[0] for station in results]

    return jsonify(station_list)

# TOBs route
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find the most active station
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]

    # Calculate the date 12 months ago from today
    a_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query temperature observations for the most active station for the previous year
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station).filter(Measurement.date >= a_year_ago).all()

    #close sussion
    session.close()
    
    # Convert the query results to a list of dictionaries
    tobs_data = [{"date": date, "temperature": tobs} for date, tobs in results]

    return jsonify(tobs_data)

# Start date route
@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
     
    # start date 
    start_date = session.query(Measurement.date).order_by(Measurement.date.asc()).first()[0]
    

    # Query min, max, and avg temperatures
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date == start_date).all()

    #close session
    session.close()
    
    # Convert the query results to a list of dictionaries
    temp_stats = [{"start_date": start_date, "TMIN": tmin, "TMAX": tmax, "TAVG": tavg} for tmin, tmax, tavg in results]
   
    return jsonify(temp_stats)

# Start/end date route
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # start and end date
    start_date = session.query(Measurement.date).order_by(Measurement.date.asc()).first()[0]
    end_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

    # Query min, max, and avg temperatures
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    #close sussion
    session.close()
    
    # Convert the query results to a list of dictionaries
    temp_stats = [{"start_date": start_date, "end_date": end_date, "TMIN": tmin, "TMAX": tmax, "TAVG": tavg} for tmin, tmax, tavg in results]

    return jsonify(temp_stats)

if __name__ == "__main__":
    app.run(debug=True)