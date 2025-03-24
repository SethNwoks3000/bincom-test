# Bincom Test Project

This is a test project for the Bincom interview. It includes:

- A Flask application (app.py)
- A MySQL database (bincom_db)
- A database backup (backup.sql)
- Required dependencies (requirements.txt)

## Setup Instructions
1. Clone the repository:
   git clone https://github.com/SethNwoks3000/bincom-test.git
   cd bincom-test

2. Install dependencies:
   pip install -r requirements.txt

3. Import the database:
   mysql -u root -p bincom_db < backup.sql

4. Run the application:
   python app.py

## License
This project is under the MIT License (LICENSE).
