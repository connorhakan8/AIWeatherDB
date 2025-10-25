# run_interactive_chat.py

# Import the class we built
from DatabaseChatbot import DatabaseChatbot
# Import the cleanup function
from dbconnectors import close_connection
import sys


def run_human_chat():
    chatbot = None  # Initialize to None
    try:
        # 1. Ask the user for the mode
        mode = ""
        while mode != "manual" and mode != "discover":
            mode = input(
                "Choose how the AI receives the database. \n"
                "Say 'manual' for a hardcoded schema (fewer API calls)\n"
                "Say 'discover' for AI schema discovery (more API calls): ")
            mode = mode.lower()
            if mode != "manual" and mode != "discover":
                print("Invalid input. Please try again.")

        # 2. Initialize the chatbot class
        print(f"Initializing chatbot in '{mode}' mode...")
        chatbot = DatabaseChatbot(mode=mode)
        print("Chatbot ready. You can now start the conversation.")

        # 3. Start the human chat loop
        responded = False
        while True:
            if responded:
                aiInput = input("\nRespond to the AI (say \"end\" to end program): ")
            else:
                aiInput = input("\nStart a conversation with the AI (say \"end\" to end program): ")

            if aiInput.lower() == "end":
                break

            responded = True

            # 4. Call the class method
            print("\nAI is thinking...")
            response_text = chatbot.ask_question(aiInput)
            print(f"\n{response_text}")

    except KeyboardInterrupt:
        print("\nUser interrupted chat.")
    except Exception as e:
        print(f"\nAn error occurred: {e}", file=sys.stderr)
    finally:
        # 5. Cleanup
        print("\nChat finished. Closing database connection.")
        close_connection()


# This makes the file runnable from the command line
if __name__ == "__main__":
    run_human_chat()
