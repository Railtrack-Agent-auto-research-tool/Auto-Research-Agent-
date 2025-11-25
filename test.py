import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
load_dotenv()

model = init_chat_model("gpt-4.1")

response = model.invoke("Why do parrots talk?")
print(response)