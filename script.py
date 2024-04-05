#Note: The openai-python library support for Azure OpenAI is in preview.
      #Note: This code sample requires OpenAI Python library version 1.0.0 or higher.
import os
from openai import AzureOpenAI


client = AzureOpenAI(
  azure_endpoint = "https://ainewsletter.openai.azure.com/",
  api_key=os.getenv("ca920090faef4b558edfd2359d3488e3"),
  api_version="2024-02-15-preview"
)

# Define the prompt
prompt = "Write a tagline for an ice cream shop."

# Create the message text
message_text = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": prompt}
]

completion = client.chat.completions.create(
  model="gpt-35-turbo-16k", # model = "deployment_name"
  messages = message_text,
  temperature=0.7,
  max_tokens=800,
  top_p=0.95,
  frequency_penalty=0,
  presence_penalty=0,
  stop=None
)

# Get the generated response
response = completion.choices[0].message
generated_text = response.content
print("Generated tagline:", generated_text)

