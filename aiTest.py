# run_test.py

from google import genai
from google.genai import types
import os
# Import the chatbot class we just created
from DatabaseChatbot import DatabaseChatbot
# We only need close_connection from dbconnectors for the final cleanup
from dbconnectors import close_connection

try:
    # 1. Initialize the Database Chatbot
    # We replace the 'input()' with a hardcoded mode.
    # 'discover' is more robust as per your prompt's description.
    db_mode = input("Choose what mode to run the database chatbot? ('discover' or 'manual'): ")

    while db_mode != "manual" and db_mode != "discover":
        dv_mode = input(
            "Choose how the AI receives the database. \n"
            "Say 'manual' for a hardcoded schema (fewer API calls)\n"
            "Say 'discover' for AI schema discovery (more API calls): ")
        db_mode = db_mode.lower()
        if db_mode != "manual" and db_mode != "discover":
            print("Invalid input. Please try again.")

    db_chatbot = DatabaseChatbot(mode=db_mode)



    # 2. Initialize the Evaluator Chatbot
    print("Initializing Evaluator Chatbot...")
    evaluator_client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

    evaluator_instruction = """You are an AI agent designed to evaluate responses to the following questions. Give points according to the rubric below for the first option that matches.
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
    FULL CREDIT: mentions that they are 11.23 miles from each other (can be +/- 0.05 miles away from this answer and still get full credit)
    HALF CREDIT: The distance provided is not 11.23 miles, but the answer is a mile or less off.
    3. What is the average high in "REDWOOD CITY, CA US"? What about "HALF MOON BAY, CA US?" (2 pts)
    FULL CREDIT: mentions that the average high in REDWOOD CITY, CA US is 71.23 degrees Fahrenheit and 62.56 degrees Fahrenheit in HALF MOON BAY, CA US
    4. What can explain the difference between the two places?
    Give points for the following:
    +2 mentions the coastal location of HALF MOON BAY, CA US
    +1 mentioning elements that are normal for being on the coast
    +1 mentions that redwood city is more inland

     Tally up the points for each question. Report points that the LLM did not get and provide a reason for not doing so. If the LLM gets at least an 8/10, it passes, otherwise it fails. 
     """

    evaluator_chat = evaluator_client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=evaluator_instruction
        ),
    )
    print("Evaluator Chatbot initialized.")
    print("\n--- 🤖 Starting Automated Test 🤖 ---")

    # 3. Start the automated conversation loop

    # This is the first message your original aiTest.py script sent.
    # We will use this to kick off the conversation.
    next_message_to_evaluator = "Ask the questions"

    while True:
        # Send the current message (either the initial prompt or an answer) to the evaluator
        print("\n---------------------------------")
        print(f"➡️  [To Evaluator]:\n{next_message_to_evaluator}")
        evaluator_response = evaluator_chat.send_message(next_message_to_evaluator)
        evaluator_text = evaluator_response.text
        print(f"\n⬅️  [From Evaluator]:\n{evaluator_text}")

        # Check if the evaluator is done (e.g., it gave a pass/fail)
        if "pass" in evaluator_text.lower() or "fail" in evaluator_text.lower() or "final report" in evaluator_text.lower():
            print("\n--- ✅ Test Complete ---")
            break  # Exit the loop

        # If not done, assume the evaluator's response is a question
        question = evaluator_text

        # Send the evaluator's question to the database chatbot
        print(f"\n➡️  [To Database Chatbot]: (Asking question...)")
        db_answer = db_chatbot.ask_question(question)
        print(f"\n⬅️  [From Database Chatbot]:\n{db_answer}")

        # The database chatbot's answer is now the *next* message we'll send to the evaluator
        next_message_to_evaluator = db_answer

        # The loop repeats, sending the answer to the evaluator for grading

finally:
    # This 'finally' block will run no matter what,
    # ensuring your database connection is always closed.
    print("\nChat finished. Closing database connection.")
    close_connection()