import os

from dotenv import load_dotenv

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(root_path, ".env"))
