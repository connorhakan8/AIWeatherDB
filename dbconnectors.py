# dbconnectors.py
import os

# pip install mysql-connector-python shapely pandas
import mysql.connector as mc
# from shapely import wkb

# 1) Connect
# These are global variables that the functions below will use.
cnx = mc.connect(
    host="localhost",
    user="root",
    password=os.environ["PASSWORD"],
    database="weatherDB",
    autocommit=True,
    allow_local_infile=True,
)
# This global cursor is used for the test query in the __main__ block
cur = cnx.cursor(dictionary=True)


def list_tables() -> list[str]:
    """Retrieve the names of all tables in the MySQL database."""
    print(" - DB CALL: list_tables()")

    # Use the global 'cnx' connection to create a new cursor
    cursor = cnx.cursor()

    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'weatherDB';
    """)

    tables = cursor.fetchall()
    cursor.close()
    return [t[0] for t in tables]


def describe_table(table_name: str) -> list[tuple[str, str]]:
    """Look up the table schema in MySQL.

    Returns:
        List of columns, where each entry is a tuple of (column_name, data_type).
    """
    print(f" - DB CALL: describe_table({table_name})")

    cursor = cnx.cursor()
    cursor.execute(f"DESCRIBE {table_name};")

    schema = cursor.fetchall()
    cursor.close()

    # DESCRIBE returns: Field, Type, Null, Key, Default, Extra
    # return [(col[0], col[1]) for col in schema]
    # More robust code (in case other columns have non-serializable types):
    return [[str(item) for item in row] for row in schema]


def execute_query(sql: str) -> list[list[str]]:
    """Execute an SQL statement, returning the results (for MySQL)."""
    print(f" - DB CALL: execute_query({sql})")

    cursor = cnx.cursor()
    cursor.execute(sql)

    results = cursor.fetchall()
    cursor.close()
    return [[str(item) for item in row] for row in results]
    #try:
    #    return results
    #except:
    #    print("A TypeError exception occurred, going to backup.")
    #    return [[str(item) for item in row] for row in results]



def close_connection():
    """Closes the global database connection."""
    print(" - DB CALL: close_connection()")
    if cur:
        cur.close()
    if cnx:
        cnx.close()


# This block only runs when you execute `python dbconnectors.py`
# It will NOT run when this file is imported by DatabaseChatbot.py
if __name__ == "__main__":
    print("--- Running dbconnectors.py as standalone script for testing ---")

    # 2) Example: run a simple query
    cur.execute("SELECT COUNT(*) AS n_stations FROM Station;")
    print(cur.fetchone())

    # Test list_tables
    print("\nTesting list_tables():")
    print(list_tables())

    # Test describe_table
    print("\nTesting describe_table():")
    print(describe_table("Readings"))
    print(describe_table("Station"))

    # Test execute_query
    print("\nTesting execute_query():")
    print(execute_query("SELECT * FROM Station LIMIT 2;"))

    # Close the connection after testing
    close_connection()
    print("--- Testing complete, connection closed ---")