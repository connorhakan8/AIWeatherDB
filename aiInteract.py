# aiInteract.py

from google import genai
from google.genai import types
import os
# Import the new close_connection function as well
from dbconnectors import list_tables, describe_table, execute_query, close_connection

try:
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

    db_tools = [list_tables, describe_table, execute_query]

    instruction = """You are a helpful chatbot that can interact with an SQL database
    for weather records, all using imperial units. You will take the users questions and turn them into SQL
    queries using the tools available. Once you have the information you need, you will
    answer the user's question using the data returned. You should be able to measure distances between two
    stations given the longitude and latitude. You should also be able to reason why 
    certain records are the way they are.

    Use list_tables to see what tables are present, describe_table to understand the
    schema, and execute_query to issue an SQL SELECT query."""

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

        if aiInput == "end":
            break
        responded = True
        resp = chat.send_message(aiInput)
        print(f"\n{resp.text}")


    # You could continue the chat here, e.g.:
    # resp = chat.send_message("What are the columns in the Station table?")
    # print(f"\n{resp.text}")

finally:
    # This 'finally' block will run no matter what,
    # ensuring your database connection is always closed.
    print("\nChat finished. Closing database connection.")
    close_connection()