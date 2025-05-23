from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_chatgpt_info(dam_name, state, missing_fields):
    prompt = f"""
You are a helpful assistant providing official, recent data on U.S. dams.
The dam is '{dam_name}' located in {state}.
The following information is missing: {', '.join(missing_fields)}.

Please provide only the requested information in a clean, readable format (e.g. bullet list or JSON).
"""

    try:
        response = client.chat.completions.create(model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3)
        return response.choices[0].message.content
    except Exception as e:
        return f"Error fetching data from ChatGPT: {e}"
