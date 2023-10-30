from langchain.chat_models import ChatOpenAI
from langchain_experimental.sql import SQLDatabaseChain
from langchain.sql_database import SQLDatabase

import pymysql
import environ

env = environ.Env()
environ.Env.read_env()
API_KEY = env("OPENAI_API_KEY")
llm = ChatOpenAI(temperature=0, openai_api_key=API_KEY)
db = SQLDatabase.from_uri(
    f"mysql+pymysql://{env('DB_USER')}:{env('DB_PASSWORD')}@{env('DB_HOST')}/{env('DB_SCHEMA')}"
)

# Setup database
from utils.database import connect_to_database, get_matching_tables, get_error_tables

# Connect to the database
connection = connect_to_database()

if connection:
    # Get matching tables and error tables
    intended_tables = [
        "bi_dimensao_tempo",
        "bi_dimensao_tempo_diario",
        "bi_fato_previsao",
        "bi_fato_ressuprimento",
        "bi_fato_venda",
        "bi_fato_venda_cliente",
        "bi_fato_venda_diario",
    ]

    matching_tables = get_matching_tables(intended_tables)
    error_tables = get_error_tables(intended_tables)

# Now you have 'connection', 'matching_tables', and 'error_tables' available for use.
