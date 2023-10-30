# Imports and Setups
import environ
from langchain.chat_models import ChatOpenAI
from langchain.sql_database import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
import pymysql

env = environ.Env()
environ.Env.read_env()
API_KEY = env("OPENAI_API_KEY")

# Connect to the Database
connection = pymysql.connect(
    host=env("DB_HOST"),
    user=env("DB_USER"),
    password=env("DB_PASSWORD"),
    db=env("DB_SCHEMA"),
)
cursor = connection.cursor()

# Query DB for Tables
cursor.execute("SHOW TABLES")
all_tables = [table[0] for table in cursor.fetchall()]

# Define and Filter Tables
intended_tables = [
    "bi_dimensao_tempo",
    "bi_dimensao_tempo_diario",
    "bi_fato_previsao",
    "bi_fato_ressuprimento",
    "bi_fato_venda",
    "bi_fato_venda_cliente",
    "bi_fato_venda_diario",
]
matching_tables = [table for table in all_tables if table in intended_tables]
error_tables = [table for table in intended_tables if table not in intended_tables]

# Setup the LLM and DB Chain
llm = ChatOpenAI(temperature=0, openai_api_key=API_KEY)
db = SQLDatabase.from_uri(
    f"mysql+pymysql://{env('DB_USER')}:{env('DB_PASSWORD')}@{env('DB_HOST')}/{env('DB_SCHEMA')}"
)
db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)


QUERY = """
Given an input question, first create a syntactically correct MYSQL query to run, then look at the results of the query and return the answer. Use the following format:
Question: [question here]
SQLQuery: [SQL query to run]
SQLResult: [result of the SQLQuery]
Answer: [final answer here]
{question}
Return JSON in a single-line without whitespaces
"""
human_message_prompt = HumanMessagePromptTemplate.from_template(QUERY)
chat_prompt = ChatPromptTemplate.from_messages([human_message_prompt])
# Run the Chain
print(f"Using tables: {', '.join(matching_tables)}")
if error_tables:
    print(f"Warning! These tables were not found: {', '.join(error_tables)}")


def get_answer(question):
    # First, you'd find out which tables you should be using.
    prompt1 = f"Given the question '{question}', which tables should we look into?"
    suggested_tables = llm.generate(
        prompt1
    )  # We might need to extract the actual tables from the response

    # Now, you'll modify the chat_prompt with the extracted tables to generate the actual SQL query.
    messages = chat_prompt.format_messages(
        text=f"Using the tables {suggested_tables}, what's the answer to the question '{question}'?"
    )
    return db_chain.run(messages)  # Updated to use the new chat prompt format


while True:
    question = input("Enter your question or 'exit' to quit: ")
    if question.lower() == "exit":
        print("Exiting...")
        break
    else:
        try:
            print(get_answer(question))
        except Exception as e:
            print(f"Damn, ran into a snag: {e}")

cursor.close()
connection.close()
