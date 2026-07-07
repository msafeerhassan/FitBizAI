from openrouter import OpenRouter
from dotenv import load_dotenv
import os, json, base64

load_dotenv()

HCAI_KEY = os.getenv("HCAI_KEY")

client = OpenRouter(
    api_key=HCAI_KEY,
    server_url="https://ai.hackclub.com/proxy/v1"
)

def encodeImg(imagePath):
    if os.path.exists(imagePath):
        with open(imagePath, "rb") as file:
            encodedStr = base64.b64encode(file.read()).decode('utf-8')
            ext = os.path.splitext(imagePath)[1].replace(".", "").lower()

            if ext == "jpg":
                ext = "jpeg"
            
            return f"data:image/{ext};base64,{encodedStr}"
    return None


def runAIdaily(SYSTEM_PROMPT, USER_PROMPT, imagePaths = None):

    userContentList = [{
        "type": "text",
        "text": USER_PROMPT
    }]

    if imagePaths:
        for path in imagePaths:
            base64URI = encodeImg(path)
            if base64URI:
                userContentList.append({
                    "type": "image_url",
                    "image_url": {
                        "url": base64URI
                    }
                })

    response = client.chat.send(
        model="qwen/qwen3-32b",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": userContentList
            }
        ],
        stream=False,
        response_format={
            "type": "json_object"
        }
    )

    content = response.choices[0].message.content
    
    return json.loads(content)