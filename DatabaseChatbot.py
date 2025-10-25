# DatabaseChatbot.py

from google import genai
from google.genai import types
import os
# We only need the tools and the close function for importing
from dbconnectors import list_tables, describe_table, execute_query, close_connection


class DatabaseChatbot:
    """
    A class that encapsulates the database AI chatbot.
    It can be initialized in 'manual' or 'discover' mode.
    """

    def __init__(self, mode):
        """
        Initializes the GenAI client and the chat model with the specified mode.
        """
        try:
            self.client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
            self.chat = None
            self._initialize_chat(mode)
            print(f"DatabaseChatbot initialized in '{mode}' mode.")
        except Exception as e:
            print(f"Failed to initialize DatabaseChatbot: {e}")
            raise

    def _initialize_chat(self, mode):
        """Private helper method to set up the chat session."""
        instruction = ""
        db_tools = []

        if mode == "discover":
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
        elif mode == "manual":
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
            raise ValueError("Invalid mode. Choose 'manual' or 'discover'.")

        self.chat = self.client.chats.create(
            model="gemini-2.5-flash-lite",
            config=types.GenerateContentConfig(
                system_instruction=instruction,
                tools=db_tools,
            ),
        )

    def ask_question(self, question_text):
        """
        Sends a question to the database chatbot and returns its text response.
        """
        if not self.chat:
            raise Exception("Chat is not initialized.")

        try:
            resp = self.chat.send_message(question_text)
            return resp.text
        except Exception as e:
            print(f"Error communicating with database chatbot: {e}")
            return f"Error: {e}"

# Note: We don't call run_ai() or close_connection() here.
# This file is now just a library.