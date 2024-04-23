#Note: The openai-python library support for Azure OpenAI is in preview.
      #Note: This code sample requires OpenAI Python library version 1.0.0 or higher.
import os
from openai import AzureOpenAI


client = AzureOpenAI(
  azure_endpoint = "https://ai-azureainewsletter886222063655.openai.azure.com/",
  api_key=os.getenv("91deb199c6544add90fd043c59404168"),
  api_version="2024-02-15-preview"
)


def generate_openai_completion(prompt):
  message_text = [
    {"role": "system", "content": "This is a text to be summarized."},
    {"role": "user", "content": prompt}
  ]

  completion = client.chat.completions.create(
    model="gpt-35-turbo",
    messages=message_text,
    temperature=0.7,
    max_tokens=800,
    top_p=0.95,
    frequency_penalty=0,
    presence_penalty=0,
    stop=None
  )
  return completion.choices[0].message['content']

# 
# import os
# from openai import AzureOpenAI
# 
# 
# client = AzureOpenAI(
#   azure_endpoint = "https://ai-azureainewsletter886222063655.openai.azure.com/",
#   api_key=os.getenv("91deb199c6544add90fd043c59404168"),
#   api_version="2024-02-15-preview"
# )
# 
# 
# 
# message_text = [{"role":"system","content":"You are an AI assistant that helps people summarize an article"},{"role":"user","content":"hi how are you"},{"role":"assistant","content":"Hello! I'm an AI assistant programmed to help people summarize articles. How can I assist you today?"}]
# 
# completion = client.chat.completions.create(
#   model="gpt-35-turbo", # model = "deployment_name"
#   messages = message_text,
#   temperature=0.7,
#   max_tokens=800,
#   top_p=0.95,
#   frequency_penalty=0,
#   presence_penalty=0,
#   stop=None
# )