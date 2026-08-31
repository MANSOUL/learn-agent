from openai import OpenAI; 
import os; 
from dotenv import load_dotenv; 

load_dotenv(); 
client = OpenAI(); 
print(client.models.list().data[0].id)