import os
from openai import AzureOpenAI
# Setup an AzureOpenAI client instance with specific credentials and endpoint
client = AzureOpenAI(
  azure_endpoint = "https://newsletter.openai.azure.com/",
  api_key = "",
  api_version = "2024-02-15-preview"
)

# Function to generate OpenAI completions for a given text prompt
def generate_openai_completion(prompt):
  message_text = [
    {"role": "system", "content": "This is a text to be summarized."},
    {"role": "user", "content": prompt}
  ]
  # Request a completion from OpenAI's chat model
  completion = client.chat.completions.create(
    model="gpt-35-turbo",  # model = "deployment_name"
    messages=message_text,
    temperature=0.4,
    max_tokens=1000,
    top_p=0.95,
    frequency_penalty=0,
    presence_penalty=0,
    stop=None
  )
  # Return the content of the first message in the response
  return completion.choices[0].message.content
