Overview
Welcome to the Chatbot project! This README will guide you through the setup process and running the project.

Prerequisites
Before running the project, ensure you have the following installed:

Python 3.x
pip (Python package installer)
Setup
Clone this repository to your local machine.
Navigate to the project directory:
bash
Copy code
cd chatbot
Install project dependencies:
Copy code
pip install -r requirements.txt
Configuration
Open the config.py file located in the fastapires directory.
Set the SQLALCHEMY_DATABASE_URL variable to your desired database URL.
Set the api_key variable to your OpenAI API key.
Running the Project
Once you have configured the necessary variables, you can run the project using the following steps:

Navigate to the project directory if you haven't already:
bash
Copy code
cd chatbot
Run the project using uvicorn:
lua
Copy code
uvicorn fastapires.main:app --reload --port 8009
The project should now be running locally on port 8009. You can access it through your web browser or make API requests as needed.
