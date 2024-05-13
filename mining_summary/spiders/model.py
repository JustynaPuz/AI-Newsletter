# Note: The openai-python library support for Azure OpenAI is in preview.
# Note: This code sample requires OpenAI Python library version 1.0.0 or higher.
import os
from openai import AzureOpenAI


client = AzureOpenAI(
  azure_endpoint = "https://newsai.openai.azure.com/",
  api_key = "8d131e954ff74d7696129872388aee0c",
  api_version = "2024-02-15-preview"
)

def generate_openai_completion(prompt):
    message_text = [
        {"role": "system", "content": "This is a text to be summarized."},
        {"role": "user", "content": prompt}
    ]


    completion = client.chat.completions.create(
        model="gpt-35-turbo",  # model = "deployment_name"
        messages=message_text,
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    return completion.choices[0].message.content
