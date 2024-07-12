import openai
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import File
import os
import openai
openai.api_key = os.environ.get('OPENAI_API_KEY')
# from langchain import LLMChain, PromptTemplate
# from langchain.llms import OpenAI


# Load the summarization pipeline from Hugging Face


# @receiver(post_save, sender=File)
# def generate_file_description(sender, instance, **kwargs):
#     if instance.file:
        
#         # Read the content of the file
#         file_path = instance.file.path
#         with open(file_path, 'rb') as f:
#             content = f.read().decode('latin-1')
        

#         # Save the description to the file object
#         # instance.description = description
#         instance.save()