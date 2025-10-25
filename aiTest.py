# aiTest.py

from google import genai
from google.genai import types
import os
# Import the new close_connection function as well
from dbconnectors import list_tables, describe_table, execute_query, close_connection

try:
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

    instruction = """You are an AI agent designed to evaluate responses to the following questions. Give points according to the rubric below for the first option that matches.
    If it doesn't match any option, give no credit.
    EXAMPLES: if there is a full credit and half credit, first see if it matches the full credit criteria. If it does, give full credit
    and do not consider any other credit options. But if the answer doesn't match the full credit criteria, check the half credit criteria. If it matches that, give half credit without
    considering any other options. If the answer still doesn't match the half credit criteria, give no credit.
    
    The exception is for rubrics in the style of
    +1 (thing)
    +2 (another thing)
    
    In this case, give a point for every thing it satisfies. So if both things are satisfied, give 3 points. 
    If only the first thing is satisfied, give one point. If nothing is satisfied, give 0 points.
    
    For questions 2 and 3, do not deduct points if "Redwood City" is said instead of "REDWOOD CITY, CA US" and/or "Half Moon Bay" is said instead of "HALF MOON BAY, CA US"
    
    If any answers are given in more than 2 decimal places, deduct a point for the first offense and then other times round the answer to two decimal places
    and give credit based on that rounded answer.
    
    If the answer presented is in another unit compared to the correct answer, convert the given answer to the units in the correct answer. Then give applicable if the answer is within .02 of the correct answer.
    EXAMPLE: if the rubric mentions 108 degrees Fahrenheit (which is 42.22 degrees Celsius) and an exact answer is needed, give credit for anything in the range of 42.2 - 42.24 degrees Celsius.
    EXAMPLE 2: If the rubric mentions 11.23 miles (which is 18.07 kilometers) for full credit but then gives half credit for not getting that answer but still being 1 mile or less away from this answer (converted into kilometers, which is 1.61 kilometers away),
    give full credit if the answer is within 1.63 kilometers of the answer. So any answer that falls in the range of 16.44 - 19.7 kilometers gets half credit in this case.
     
    Questions to ask the LLM:
    
    1. On September 1, 2017, how high did it get in Redwood City? (2 pts)
    FULL CREDIT: mentions that it reached 108 degrees Fahrenheit
    2. How far away are "REDWOOD CITY, CA US" and "HALF MOON BAY, CA US" from each other? (2 pts)
    FULL CREDIT: mentions that they are 11.23 miles from each other
    HALF CREDIT: The distance provided is not 11.23 miles, but the answer is a mile or less off.
    3. What is the average high in "REDWOOD CITY, CA US" and "HALF MOON BAY, CA US? (2 pts)
    FULL CREDIT: mentions that the average high in REDWOOD CITY, CA US is 71.23 degrees Fahrenheit and 62.56 degrees Fahrenheit in HALF MOON BAY, CA US
    4. What can explain the difference between the two places?
    Give points for the following:
    +2 mentions the coastal location of HALF MOON BAY, CA US
    +1 mentioning fog
    +1 mentions that redwood city is more inland
     
     Tally up the points for each question. Report points that the LLM did not get and provide a reason for not doing so. If the LLM gets at least an 8/10, it passes, otherwise it fails. 
     """

    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=instruction
        ),
    )

    chat.send_message("Ask the questions")


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