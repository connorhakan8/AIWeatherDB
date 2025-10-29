# AI Weather Database

## Important notices
The code will probably not run in its current state because the CSV that generates the data needs to be set to the appropriate location. 
In my setup, despite having it in the same file as my SQL file, the SQL would not run and acted like the file could not be found.
So the CSV therefore needs to be set to the location based off the root directory.
You'll need to set the SQL up on your own database and will need your own password to access it.
Similarly, you'll also need your own Google API key.


## Project overview
This is a database project I made where I grabbed 10 years of temperature data from places in and near the San Francisco Bay Area in California and made it accessible to an AI agent based on the Google GenAI SDK.
The AI agent knows that it has access to the database via a few tools, like getting a list of all tables, getting the datatypes of everything in the table, and being able to execute SQL queries.
The AI agent is able to answer generic questions about the table, like ('what is the highest temperature recorded in San Francisco in 2017'). 
But each station also has coordinates and elevation, which allows the AI to better explore the complexity of the Bay Area's climate (for those who don't know, the Bay Area has many microclimates).
You can ask the agent 'What two stations are close to each other that have significant differences in temperature and reason why' and it can find two weather stations that are close to one another.
There are many other ways the AI can explore the database, so ask away!
Another feature includes LLM testing, in which one AI agent will quiz another AI agent on a suite of questions (LLM testing LLM) and grade it based on various criteria, such as if it mentioned something in its response, overall getting a conclusion on if the agent passes the test suite or not. In such, we see if the LLM model the agent is based on is suitable in answering questions.
Maybe in the future I will grab temperature data from all across California for use in the database (would be harder to add precipitation because there's a limited number of stations with both temperature and precipitation).
