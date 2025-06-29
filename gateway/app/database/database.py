from supabase import create_client, Client
from os       import environ

database: Client = create_client(
    environ.get('SUPABASE_ENDPOINT'),
    environ.get('SUPABASE_KEY')
)