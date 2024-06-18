
# Steps to Run Files

## Getting Started
These instructions will guide you on how to set up and run the project.

### Prerequisites
You need to have PostgreSQL installed and Python with necessary libraries.

### Steps
1. **Clone the Repository**
    ```bash
    git clone [repository-url]
    ```
2. **Extract the Files**
    Extract the files from the downloaded ZIP folder.
3. **Change Directory**
    ```bash
    cd [project-folder]
    ```
4. **Database Setup**
    Connect to PostgreSQL and create a database named `receipts_database`:
    ```sql
    CREATE DATABASE receipts_database;
    ```
5. **Run Data Load Script**
    Modify the connection details in `dataload.py` and run:
    ```bash
    python dataload.py
    ```
6. **Run SQL Queries**
    Connect to the PostgreSQL database and execute the SQL queries found in `DataAnalysis.sql`.
7. **Data Quality Checks**
    Run the data quality checks:
    ```bash
    python dq_checks.py
    ```
8. **Data Model Visualization**
    Review the data model in `Receipts.png`.
9. **Business Communication**
    Review and send the email prepared in `Email_draft` file.

## Support
For any additional information or support, contact [your-email].
