"""Central settings, loaded once from the .env file."""
import os

from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", "llama3.2:3b")
RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))
