import os

# openai
def import_client():
    # api_key = os.environ["OPENAI_API_KEY"]
    from openai import OpenAI
    from dotenv import load_dotenv
    load_dotenv()
    return OpenAI()

def interact_with_agent(llm_client, messages, model):
    response = llm_client.chat.completions.create(
            model=model,
            messages=messages
        )
    return response.choices[0].message.content


