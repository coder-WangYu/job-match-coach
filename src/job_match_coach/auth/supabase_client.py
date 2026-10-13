from dotenv import load_dotenv
from supabase import create_client
import os

def get_supabase():
    load_dotenv()

    return create_client(
        os.environ.get("SUPABASE_URL"),
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    )