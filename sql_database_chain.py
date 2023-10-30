import environ

from langchain.chat_models import ChatOpenAI
from langchain_experimental.sql import SQLDatabaseChain
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
# connection = connect_to_database()

# if connection:
#     intended_tables = [
#         "bi_dimensao_tempo",
#         "bi_dimensao_tempo_diario",
#         "bi_fato_previsao",
#         "bi_fato_ressuprimento",
#         "bi_fato_venda",
#         "bi_fato_venda_cliente",
#         "bi_fato_venda_diario",
#     ]

#     matching_tables = get_matching_tables(intended_tables)
#     error_tables = get_error_tables(intended_tables)

QUERY = """
Given an input question, first create a syntactically correct postgresql query to run, then look at the results of the query and return the answer.
Use the following format:

Question: Question here
SQLQuery: SQL Query to run
SQLResult: Result of the SQLQuery
Answer: Final answer here

{question}
"""

db_chain = SQLDatabaseChain.from_llm(llm=llm, db=db, verbose=True)


def get_prompt():
    print("Type 'exit' to quit")

    while True:
        prompt = input("Enter a prompt: ")

        if prompt.lower() == "exit":
            print("Exiting...")
            break
        else:
            try:
                question = QUERY.format(question=prompt)
                print(db_chain.run(question))
            except Exception as e:
                print(e)


get_prompt()
