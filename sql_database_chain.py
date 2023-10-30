import environ

from langchain.schema import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain_experimental.sql.base import SQLDatabaseSequentialChain
from utils.mysql_db import (
    connect_to_database,
    get_matching_tables,
    get_error_tables,
    setup_database,
)

env = environ.Env()
environ.Env.read_env()
API_KEY = env("OPENAI_API_KEY")

llm = ChatOpenAI(temperature=0, openai_api_key=API_KEY)
db = setup_database()

connection = connect_to_database()
cursor = connection.cursor()
if connection:
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
    matching_tables_str = ", ".join(matching_tables)
    if matching_tables:
        print(f"Using tables: {', '.join(matching_tables)}")
    error_tables = get_error_tables(intended_tables)
    if error_tables:
        print(f"Warning! These tables were not found: {', '.join(error_tables)}")

QUERY = """
Given an input question, first create a syntactically correct MYSQL query to run, then look at the results of the query and return the answer. Use the following format:
Question: [question here]
SQLQuery: [SQL query to run]
SQLResult: [result of the SQLQuery]
Answer: [final answer here]
{question}
You'll only use the following tables on your reasoning: {matching_tables_str}
Return JSON in a single-line without whitespaces
The final answer MUST be in Brazilian Portuguese
BEGIN!
"""

db_chain = SQLDatabaseSequentialChain.from_llm(llm=llm, db=db, verbose=True)
output_parser = StrOutputParser()
question = "Qual foi a quantidade de ressuprimento no dia 2021-11-18?"


def get_suggested_tables(question):
    try:
        question = QUERY.format(
            matching_tables_str=matching_tables_str, question=question
        )
        print(db_chain.run(question))
    except Exception as e:
        print(f"Exception: {e}")


get_suggested_tables(question)

connection.close()
cursor.close()
