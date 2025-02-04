import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the variables
api_key = os.getenv("LOG_FOLDER_PATH")
print(api_key)