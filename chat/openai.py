from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.messages import SystemMessage,HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
import json
import threading
import asyncio
import json
from asgiref.sync import sync_to_async

parser = StrOutputParser()
model = ChatOpenAI(model="gpt-3.5-turbo")

from chat.models import Folder
@sync_to_async
def get_model_objects():
    return list(Folder.objects.all())


def call_model(prompt_template, django_objects, user_query):
    chain = prompt_template | model | parser
    return chain.invoke({"django_objects": django_objects, "user_query": user_query})


async def get_intent_scores(user_query):
    django_objects = await get_model_objects()
    # print(django_objects)
    prompt = """
    Task: You are given a list of Django model objects. Each object has a 'description' field. Your task is to
    1. Extract the 'description' field from each object.
    2. Understand the intent of the given user input query.
    3. Match the intent of the user query with each folder description.
    4. Return a dictionary where the keys are the 'name' values of the objects (treated as folder names) and the values are intent scores that indicate how well the user query matches each folder description
    Scoring should be on a scale from 0 to 1, where 1 means a perfect match and 0 means no match
    Example
    Given Django model objects:
    [
      {{"id": 2,"name": "ProCare","description" :"This folder contains all the documents related to the Pro Care project." ,"parent_id": "1"}},
      {{"id": 3,"name": "Financials","description" : "This folder contains financial reports and documents related to the Pro Care project.","parent_id": "1"}}
    ]

    User input query: "Where can I find the financial documents?
    Expected Output:
    {{
      "Reports": 0.5,
      "Invoices": 0.9,
      "Receipts": 0.7
    }}
    Now, given the following Django model objects and user input query, provide the required dictionary
    Django model objects:
    {django_objects}
    """
    
    prompt_template = ChatPromptTemplate.from_messages(
    [("system", prompt), ("user", f"{user_query}")]
    )

    # chain = prompt_template | model | parser
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit the function to the executor
        future = executor.submit(call_model, prompt_template, django_objects, user_query)
        
        # Fetch the result from the future
        result = future.result()

    dic_result = json.loads(result)
    return dic_result


