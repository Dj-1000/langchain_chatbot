GET_FOLDER_INTENT_PROMPT="""
Task: You are given a list of Django model objects named 'Folder'. Each object has a 'description' field. Your task is to:
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
User input query: "I want the to know about the project timelines."
Expected Output:
{{
  "is_match": False,
  "message": "I'm sorry, but I didn't quite understand that. Could you please provide more details about the file or folder you're looking for?",
  "category": "null"
}}
User input query: "I want the to know about the project tiimelines."
Expected Output:
{{
  "is_match": False,
  "message": "I'm sorry, but I didn't quite understand that. Could you please provide more details about the file or folder you're looking for?",
  "category": "null"
}}

In case the 'is_match' field is FALSE. Here are some examples of fallback responses to gather more information:

a. "I'm sorry, but I didn't quite understand that. Could you please provide more details about the file or folder you're looking for?"
b. "Can you please clarify what you're looking for? Any additional information about the file or folder would help."
c. "I'm having trouble understanding your request. Could you describe the file or folder in more detail?"
d. "Could you please provide the name or a part of the name of the file or folder?"
e. "Do you know the location or directory where the file or folder might be?"
f. "Can you tell me the type of file or any specific keywords associated with it?"


In case the 'is_match' field is TRUE. Here are some examples of fallback responses to gather more information:

Now, given the following Django model objects and user input query, provide the required dictionary:
Django model objects: {django_objects}
"""


GET_FILE_INTENT_PROMPT = """
Task: You are given a list of Django file objects. Each object has a 'description' field. Your task is to:
1. Extract the 'description' field from each file object.
2. Understand the intent of the given user input query.
3. Match the intent of the user query with each file description.
4. Return a structured output with the following keys:
   - is_match: Boolean, set to True if any file intent score is more than 0.7.
   - message: String, a message asking for more details if 'is_match' is False, or requesting confirmation if 'is_match' is True.
   - file_name: String, the name of the file with the highest intent score, or null if no match.
   - category: String, the category of the parent folder, or null if no match.
   - link : String, the url of the file field of the file objects with highest intent score, or null if no ma
Scoring should be on a scale from 0 to 1, where 1 means a perfect match and 0 means no match
Example
Given Django file objects:
[
  {{"id": 1, "name": "Report.pdf", "description": "This file contains the annual report for the Pro Care project.", "folder": "Financials"}},
  {{"id": 2, "name": "Budget.xlsx", "description": "This file contains the budget details for the Pro Care project.", "folder": "Financials"}}

User input query: "Where can I find the budget detail
Expected Output:
{{
  "is_match": True,
  "message": "Is 'Budget.xlsx' the file you are looking for?",
  "file_name": "Budget.xlsx",
  "file_id": "45"
  "category": "123"

Example
Given Django file objects:
[
  {{"id": 1, "name": "Report.pdf", "description": "This file contains the annual report for the Pro Care project.", "folder": "Financials"}},
  {{"id": 2, "name": "Budget.xlsx", "description": "This file contains the budget details for the Pro Care project.", "folder": "Financials"}}

User input query: "Where can I find the project timeline
Expected Output:
{{
  "is_match": False,
  "message": "Please provide more details or be more specific about the file you are looking for.",
  "file_name": "null",
   "file_id": "null",
  "category": "null"

Example
Given Django file objects:
[
  {{"id": 1, "name": "Report.pdf", "description": "This file contains the annual report for the Pro Care project.", "folder": "Financials"}},
  {{"id": 2, "name": "Budget.xlsx", "description": "This file contains the budget details for the Pro Care project.", "folder": "Financials"}}

User input query: "Show me the documen
Expected Output:
{{
  "is_match": False,
  "message": "Please start again and provide more specific details.",
  "file_name": "null",
  "category": "null"

Now, given the following Django file objects and user input query, provide the required dictiona
Django file objects: {file_objects}
"""