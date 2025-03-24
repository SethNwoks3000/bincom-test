from flask import Flask, render_template, request
import mysql.connector
from dotenv import load_dotenv
import os

app = Flask(__name__)

#configurations
load_dotenv()

db_config = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE")
}

def get_db_connection():
    """Create and return a new database connection"""
    return mysql.connector.connect(**db_config)

@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch polling units that have results
    cursor.execute("""
        SELECT DISTINCT CAST(p.uniqueid AS CHAR) 
        FROM polling_unit p
        JOIN announced_pu_results r 
        ON p.uniqueid = r.polling_unit_uniqueid
    """)
    polling_units = [row[0] for row in cursor.fetchall()]

    # Fetch LGAs that have results
    cursor.execute("""
        SELECT DISTINCT l.lga_id, l.lga_name 
        FROM lga l
        JOIN polling_unit p ON l.lga_id = p.lga_id
        JOIN announced_pu_results r ON p.uniqueid = r.polling_unit_uniqueid
    """)
    lgas = cursor.fetchall()

    # Fetch wards that have results
    cursor.execute("""
        SELECT DISTINCT w.ward_id, w.ward_name 
        FROM ward w 
        JOIN polling_unit p ON w.ward_id = p.ward_id 
        JOIN announced_pu_results r ON p.uniqueid = r.polling_unit_uniqueid
    """)
    wards = cursor.fetchall()

    results = []
    selected_polling_unit = None
    selected_lga = None
    selected_ward = None

    if request.method == "POST":
        if "polling_unit" in request.form:
            selected_polling_unit = request.form["polling_unit"]
            cursor.execute("""
                SELECT party_abbreviation, party_score 
                FROM announced_pu_results 
                WHERE polling_unit_uniqueid = %s
            """, (selected_polling_unit,))
            results = cursor.fetchall()

        elif "lga" in request.form:
            selected_lga = request.form["lga"]
            cursor.execute("SELECT uniqueid FROM polling_unit WHERE lga_id = %s", (selected_lga,))
            polling_units_in_lga = [row[0] for row in cursor.fetchall()]

            if polling_units_in_lga:
                format_strings = ','.join(['%s'] * len(polling_units_in_lga))
                cursor.execute(f"""
                    SELECT party_abbreviation, SUM(party_score) 
                    FROM announced_pu_results 
                    WHERE polling_unit_uniqueid IN ({format_strings}) 
                    GROUP BY party_abbreviation
                """, tuple(polling_units_in_lga))
                results = cursor.fetchall()

        elif "ward" in request.form:
            selected_ward = request.form["ward"]
            cursor.execute("SELECT uniqueid FROM polling_unit WHERE ward_id = %s", (selected_ward,))
            polling_units = [row[0] for row in cursor.fetchall()]

            if polling_units:
                format_strings = ','.join(['%s'] * len(polling_units))
                cursor.execute(f"""
                    SELECT party_abbreviation, SUM(party_score) 
                    FROM announced_pu_results 
                    WHERE polling_unit_uniqueid IN ({format_strings}) 
                    GROUP BY party_abbreviation
                """, tuple(polling_units))
                results = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template(
        "index.html",
        polling_units=polling_units,
        lgas=lgas,
        wards=wards,
        results=results,
        selected_polling_unit=selected_polling_unit,
        selected_lga=selected_lga,
        selected_ward=selected_ward
    )

if __name__ == "__main__":
    app.run(debug=True)
