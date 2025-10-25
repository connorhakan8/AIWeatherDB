# aiInteract.py

from google import genai
from google.genai import types
import os
# Import the new close_connection function as well
from dbconnectors import list_tables, describe_table, execute_query, close_connection
def run_ai():
    try:
        client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

        db_tools = []

        firstResponse = ""
        instruction = ""
        while firstResponse != "manual" and firstResponse != "discover":
            firstResponse = input(
                "Choose how the AI receives the database. \nSay 'manual' if you want the AI to be provided "
                "the database (does not respond to changes in database schema but reduces API calls)\n"
                "Say 'discover' for the AI to discover the database (responds to changes in database schema but "
                "increases API calls): ")
            firstResponse = firstResponse.lower()
            if firstResponse == "discover":
                instruction = """You are a helpful chatbot that can interact with an SQL database
                       for weather records, all using imperial units. You will take the users questions and turn them into SQL
                       queries using the tools available. Once you have the information you need, you will
                       answer the user's question using the data returned. Any temperatures or distances given should have no more than 2 decimal places. 
                       (no trailing zeroes though). You should be able to measure distances between two
                       stations given the longitude and latitude with manual calculations (but this details in 
                    calculating should not be shown to the user). You should also be able to reason why 
                       certain records are the way they are.

                       Use list_tables to see what tables are present, describe_table to understand the
                       schema, and execute_query to issue an SQL SELECT query."""
                db_tools = [list_tables, describe_table, execute_query]
            elif firstResponse == "manual":
                instruction = """You are a helpful chatbot that can interact with an SQL database
                    for weather records, all using imperial units. 
                    If you need to construct SQL queries, you MUST use the following database schema:

                    STATION
                      stationID   VARCHAR(11) PRIMARY KEY,
                      stationName VARCHAR(45) NOT NULL,
                      location    POINT NOT NULL SRID 4326,
                      elevation   DECIMAL(7,2)

                    READINGS
                      stationID   VARCHAR(11) NOT NULL,
                      readingDate DATE NOT NULL,
                      dailyHigh   SMALLINT,
                      dailyLow    SMALLINT,
                      CONSTRAINT PK_READINGS PRIMARY KEY (stationID, readingDate),
                      CONSTRAINT FK_READING_STATION
                        FOREIGN KEY (stationID) REFERENCES Station(stationID)
                        ON DELETE CASCADE

                    You will take the users questions and turn them into SQL
                    queries using the tools available. Once you have the information you need, you will
                    answer the user's question using the data returned. Any temperatures or distances given should have no more than 2 decimal places
                    (no trailing zeroes though). Don't be alarmed if you cannot find a station; 
                    users might put station names that are similar, but not exact
                    to what is represented in the database; you might need to use the LIKE operator 
                    in this case to find the actual name in the database.

                    You should be able to measure distances between two
                    stations given the longitude and latitude with manual calculations (but this details in 
                    calculating should not be shown to the user). Your capabilities should extend
                    beyond just querying the weather database; you should also be able to reason why 
                    certain records are the way they are.

                    Use execute_query to run SQL queries."""
                db_tools = [execute_query]
            else:
                print("Invalid input. Please try again.")

            # if firstResponse.lower() != "manual" and firstResponse.lower() != "discover":
            #     print(firstResponse)
            #     print("Invalid response. Please try again.")
            # elif firstResponse == "discover":
            #     instruction = """You are a helpful chatbot that can interact with an SQL database
            #         for weather records, all using imperial units. You will take the users questions and turn them into SQL
            #         queries using the tools available. Once you have the information you need, you will
            #         answer the user's question using the data returned. You should be able to measure distances between two
            #         stations given the longitude and latitude with manual calculations. You should also be able to reason why
            #         certain records are the way they are.
            #
            #         Use list_tables to see what tables are present, describe_table to understand the
            #         schema, and execute_query to issue an SQL SELECT query."""
            # else: # manual

        chat = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=instruction,
                tools=db_tools,
            ),
        )
        responded = False
        while True:
            if responded:
                aiInput = input("Respond to the AI (say \"end\" to end program): ")
            else:
                aiInput = input("Start a conversation with the AI (say \"end\" to end program): ")

            if aiInput.lower() == "end":
                break
            responded = True
            resp = chat.send_message(aiInput)
            print(f"\n{resp.text}")

    finally:
        # This 'finally' block will run no matter what,
        # ensuring your database connection is always closed.
        print("\nChat finished. Closing database connection.")
        close_connection()

run_ai()