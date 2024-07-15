from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.chains.openai_functions.qa_with_structure import create_qa_with_structure_chain
from langchain_core.pydantic_v1 import BaseModel, Field
# from langchain.memory import InMemoryVariableManager
from langchain_core.output_parsers import StrOutputParser

import random
from django.db.models import Q
import uuid
import json
from asgiref.sync import sync_to_async
from .models import Room, File
import concurrent.futures

parser = StrOutputParser()
model = ChatOpenAI(model="gpt-4")

from chat.models import Folder


class IntentScoreOutput(BaseModel):
    """description"""
    is_match: bool = Field(..., description="Boolean, set to True if the highest intent score is more than 0.5.")
    message: str = Field(..., description="A message asking for more details if 'is_match' is False.")
    category: int = Field(..., description="The id of the folder with the highest intent score.")

class FileIntentScoreOutput(BaseModel):
    """dis"""
    is_match: bool = Field(..., description="Boolean, set to True if any file intent score is more than 0.7.")
    message: str = Field(..., description="A message asking for more details if 'is_match' is False or requesting confirmation if 'is_match' is True.")
    file_name: str = Field(..., description="The name of the file with the highest intent score, or null if no match.")
    category: str = Field(..., description="The category of the parent folder, or null if no match.")

@sync_to_async
def get_folder_objects(id=None):
    folders_with_files = Folder.objects.prefetch_related('files').all()
    if id is not None:
        obj = Folder.objects.filter(id=id).first()
        return obj
    return list(Folder.objects.all())

@sync_to_async
def get_folder_files(folder_id):
    if folder_id:
        files = File.objects.filter(folder_id = folder_id).all()
        return files

@sync_to_async
def room_session_update(category = None,is_matched=None):
    ##first you have to get a room with an id to update and for that you must save id somewhere 
    session = Room.objects.last()
    if session:
        folder = Folder.objects.filter(id = category).first()
        session.category = folder
        session.is_matched = is_matched
        session.save()
    
    
    
@sync_to_async
def check_session(room_name = None):
    room = Room.objects.filter(id = room_name).first()
    if room:
        return room.is_matched
    

@sync_to_async
def get_current_room(room_name):
    room = Room.objects.filter(id = room_name).first()
    return room




def call_model(prompt_template,django_objects,user_query,schema=IntentScoreOutput):

    # Create the chain with structured output
    # chain = prompt_template | model | parser
    chain = create_qa_with_structure_chain(
        llm=model,
        prompt=prompt_template,
        schema=schema
    )
    result = chain.invoke({"django_objects": django_objects, "user_query": user_query})
    result = json.loads(result.get('text'))
    # Handle the structured output
    if result['is_match']:
        return result
    else:
        return result



async def get_intent_scores(user_query,room_name):

    category = await check_session(room_name)

    if category:
        return await bot_conversation(user_query,room_name=room_name)

    django_objects = await get_folder_objects()

    # print(django_objects)
    prompt = """
    Task: You are given a list of Django model objects. Each object has a 'description' field. Your task is to:
    1. Extract the 'description' field from each object.
    2. Understand the intent of the given user input query.
    3. Match the intent of the user query with each folder description.
    4. Return a structured output with the following keys:
       - is_match: Boolean, set to True if the highest intent score is more than 0.5.
       - message: String, a message asking for more details if 'is_match' is False.
       - category: Integer, the id of the folder with the highest intent score.

    Scoring should be on a scale from 0 to 1, where 1 means a perfect match and 0 means no match.

    Example 1:

    Given Django model objects:
    [
      {{"id": 2, "name": "ProCare", "description": "This folder contains all the documents related to the Pro Care project.", "parent_id": "1"}},
      {{"id": 3, "name": "Financials", "description": "This folder contains financial reports and documents related to the Pro Care project.", "parent_id": "1"}}
    ]

    User input query: "Where can I find the financial documents?"

    Expected Output:
    {{
      "is_match": True,
      "message": "Please provide more details about the financial documents you are looking for in the Financials category.",
      "category": "123"
    }}

    Example 2:

    Given Django model objects:
    [
      {{"id": 2, "name": "ProCare", "description": "This folder contains all the documents related to the Pro Care project.", "parent_id": "1"}},
      {{"id": 3, "name": "Financials", "description": "This folder contains financial reports and documents related to the Pro Care project.", "parent_id": "1"}}
    ]

    User input query: "Where can I find the project timelines?"

    Expected Output:
    {{
      "is_match": False,
      "message": "Please provide more details or be more specific about what exactly you are asking.",
      "category": "null"
    }}

    Now, given the following Django model objects and user input query, provide the required dictionary:

    Django model objects: {django_objects}
    """ 
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system",prompt),
            ("user","{user_query}")
        ]
    )
    # chain = prompt_template | model | parser
   
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit the function to the executor
        future = executor.submit(call_model,prompt_template,django_objects, user_query)
        
        # Fetch the result from the future
        result = future.result()

    if result['is_match']:
        await room_session_update(category = result['category'],is_matched=True)
        return result['message']
    return result['message']




async def bot_conversation(user_query,room_name):
    room = await get_current_room(room_name)
    folder_id = room.category_id
    # folder = await get_folder_objects(id = folder_id)
    django_objects = await get_folder_files(folder_id)

    # Define the prompt template
    prompt_template = ChatPromptTemplate.from_messages(
        [ ("system", """
        Task: You are given a list of Django file objects. Each object has a 'description' field. Your task is to:
        1. Extract the 'description' field from each file object.
        2. Understand the intent of the given user input query.
        3. Match the intent of the user query with each file description.
        4. Return a structured output with the following keys:
           - is_match: Boolean, set to True if any file intent score is more than 0.7.
           - message: String, a message asking for more details if 'is_match' is False, or requesting confirmation if 'is_match' is True.
           - file_name: String, the name of the file with the highest intent score, or null if no match.
           - category: String, the category of the parent folder, or null if no match.

        Scoring should be on a scale from 0 to 1, where 1 means a perfect match and 0 means no match.

        Example 1:

        Given Django file objects:
        [
          {{"id": 1, "name": "Report.pdf", "description": "This file contains the annual report for the Pro Care project.", "folder": "Financials"}},
          {{"id": 2, "name": "Budget.xlsx", "description": "This file contains the budget details for the Pro Care project.", "folder": "Financials"}}
        ]

        User input query: "Where can I find the budget details?"

        Expected Output:
        {{
          "is_match": True,
          "message": "Is 'Budget.xlsx' the file you are looking for?",
          "file_name": "Budget.xlsx",
          "category": "Financials"
        }}

        Example 2:

        Given Django file objects:
        [
          {{"id": 1, "name": "Report.pdf", "description": "This file contains the annual report for the Pro Care project.", "folder": "Financials"}},
          {{"id": 2, "name": "Budget.xlsx", "description": "This file contains the budget details for the Pro Care project.", "folder": "Financials"}}
        ]

        User input query: "Where can I find the project timelines?"

        Expected Output:
        {{
          "is_match": False,
          "message": "Please provide more details or be more specific about the file you are looking for.",
          "file_name": null,
          "category": null
        }}

        Example 3:

        Given Django file objects:
        [
          {{"id": 1, "name": "Report.pdf", "description": "This file contains the annual report for the Pro Care project.", "folder": "Financials"}},
          {{"id": 2, "name": "Budget.xlsx", "description": "This file contains the budget details for the Pro Care project.", "folder": "Financials"}}
        ]

        User input query: "Show me the documents"

        Expected Output:
        {{
          "is_match": False,
          "message": "Please start again and provide more specific details.",
          "file_name": null,
          "category": null
        }}

        Now, given the following Django file objects and user input query, provide the required dictionary:

        Django file objects: {django_objects}
        """), 
        ("user", "{user_query}")]
    )

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit the function to the executor
        future = executor.submit(call_model,prompt_template, django_objects, user_query,schema = FileIntentScoreOutput)
        
        # Fetch the result from the future
        result = future.result()

    if result['is_match']:
        # await room_session_update(category = result['category'],is_matched=True)
        return result['message']
    
    return result['message']


    

    