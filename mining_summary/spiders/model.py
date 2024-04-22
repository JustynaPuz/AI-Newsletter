# #Note: The openai-python library support for Azure OpenAI is in preview.
#       #Note: This code sample requires OpenAI Python library version 1.0.0 or higher.
# import os
# from openai import AzureOpenAI
#
#
# client = AzureOpenAI(
#   #azure_endpoint = "https://ainewsletter.openai.azure.com/",
#   api_key=os.getenv("ca920090faef4b558edfd2359d3488e3"),
#   api_version="2024-02-15-preview",
#   azure_endpoint = os.getenv("https://ainewsletter.openai.azure.com/")
# )
#
#
# def generate_openai_completion(prompt):
#   message_text = [
#     {"role": "system", "content": "This is a text to be summarized."},
#     {"role": "user", "content": prompt}
#   ]
#
#   completion = client.chat.completions.create(
#     model="gpt-3.5-turbo",
#     messages=message_text,
#     temperature=0.7,
#     max_tokens=800,
#     top_p=0.95,
#     frequency_penalty=0,
#     presence_penalty=0,
#     stop=None
#   )
#   return completion.choices[0].message['content']

import os
from openai import AzureOpenAI

client = AzureOpenAI(
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version="2024-02-15-preview",
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
)

deployment_name = 'gpt-3.5-turbo-16k'  # This will correspond to the custom name you chose for your deployment when you deployed a model. Use a gpt-35-turbo-instruct deployment.

# Send a completion call to generate an answer
print('Sending a test completion job')
start_phrase = 'Write a tagline for an ice cream shop. '
response = client.completions.create(model=deployment_name, prompt=start_phrase, max_tokens=10)
print(start_phrase + response.choices[0].text)