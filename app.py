from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def get_cecil_zipcodes():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT zipcode FROM zipcode_lookup WHERE county = 'Cecil County'")
    zipcodes = [row[0] for row in cursor.fetchall()]
    conn.close()
    return zipcodes

def get_covid_cases(zipcode, date):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # First, verify that the zipcode is in Cecil County
    cursor.execute("SELECT county FROM zipcode_lookup WHERE zipcode = ?", (zipcode,))
    result = cursor.fetchone()
    if not result or result[0] != 'Cecil':
        logging.debug(f"Zipcode {zipcode} is not in Cecil County.")
        conn.close()
        return None

    # Get the date column name
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    date_column = date_obj.strftime('%Y-%m-%d')
    
    # Get the zipcode column name with the "z_" prefix
    zipcode_column = f"z_{zipcode}"
    
    # Query for the cases
    try:
        query = f"""
            SELECT "{zipcode_column}" 
            FROM Feb2022_Covid_Cases_in_MD_byZipcode 
            WHERE date = ?
        """
        logging.debug(f"Executing query: {query} with date: {date_column}")
        cursor.execute(query, (date_column,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            logging.debug(f"Query result: {result[0]}")
        else:
            logging.debug("No results found for the query.")
        
        return result[0] if result else None
    except sqlite3.OperationalError as e:
        logging.error(f"SQL Error: {e}")
        conn.close()
        return None

def generate_graph(zipcode, date, cases):
    plt.figure(figsize=(10, 5))
    plt.bar([date], [cases], color='blue')
    plt.xlabel('Date')
    plt.ylabel('Number of Cases')
    plt.title(f'COVID-19 Cases for Zip Code {zipcode} on {date}')
    graph_path = f'static/graphs/{zipcode}_{date}.png'
    plt.savefig(graph_path)
    plt.close()
    return graph_path

def print_table_schema_and_sample_data():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # Print the schema of the table
    cursor.execute("PRAGMA table_info(Feb2022_Covid_Cases_in_MD_byZipcode)")
    schema = cursor.fetchall()
    logging.debug("Table schema:")
    for column in schema:
        logging.debug(column)
    
    # Print some sample data
    cursor.execute("SELECT * FROM Feb2022_Covid_Cases_in_MD_byZipcode LIMIT 5")
    sample_data = cursor.fetchall()
    logging.debug("Sample data:")
    for row in sample_data:
        logging.debug(row)
    
    conn.close()

@app.route('/', methods=['GET'])
def index():
    cecil_zipcodes = get_cecil_zipcodes()
    
    # Generate list of dates for February 2022
    start_date = datetime(2022, 2, 1)
    end_date = datetime(2022, 2, 28)
    dates = [(start_date + timedelta(days=x)).strftime('%Y-%m-%d') for x in range((end_date - start_date).days + 1)]
    
    return render_template('index.html', zipcodes=cecil_zipcodes, dates=dates)

@app.route('/search', methods=['POST'])
def search():
    zipcode = request.form['zipcode']
    date = request.form['date']
    logging.debug(f"Search request received for zipcode: {zipcode}, date: {date}")
    cases = get_covid_cases(zipcode, date)
    if cases is not None:
        graph_url = generate_graph(zipcode, date, cases)
        logging.debug(f"Graph generated at: {graph_url}")
        return jsonify({"success": True, "cases": cases, "graph_url": graph_url})
    else:
        logging.debug("No data found for the given Cecil County zipcode and date.")
        return jsonify({"success": False, "message": "No data found for the given Cecil County zipcode and date."})

if __name__ == '__main__':
    if not os.path.exists('static/graphs'):
        os.makedirs('static/graphs')
    print_table_schema_and_sample_data()
    app.run(debug=True)