from langchain.llms import OpenAI

import environ

env = environ.Env()
environ.Env.read_env()
API_KEY = env("OPENAI_API_KEY")

from langchain.prompts import PromptTemplate
from langchain import LLMChain

llm = OpenAI(temperature=0, openai_api_key=API_KEY)
template = "What are the top {n} resources to learn {language} programming?"
prompt = PromptTemplate(template=template, input_variables=["n", "language"])
chain = LLMChain(llm=llm, prompt=prompt)
input = {"n": 5, "language": "python"}
print(chain.run(input))
