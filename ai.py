from openrouter import OpenRouter
from dotenv import load_dotenv
import os, json

load_dotenv()

HCAI_KEY = os.getenv("HCAI_KEY")

client = OpenRouter(
    api_key=HCAI_KEY,
    server_url="https://ai.hackclub.com/proxy/v1"
)


def runAIdaily(SYSTEM_PROMPT, USER_PROMPT):
    response = client.chat.send(
        model="qwen/qwen3-32b",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": USER_PROMPT
            }
        ],
        stream=False,
        response_format={
            "type": "json_object"
        }
    )

    content = response.choices[0].message.content
    
    return json.loads(content)