# server/config.py
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = "sqlite:///user.db"
# DATABASE_URL="postgresql://postgres:1234@localhost:5432/dbchatbot"

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
NVIDIA_API_KEY = os.getenv('NVIDIA_API_KEY')

LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')
TELEGRAM_SECRET_KEY = os.getenv('TELEGRAM_SECRET_KEY')
