import asyncio
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

async def test_native_search():
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    keyword = "두바이 쫀득쿠키"
    
    print(f"Testing Native Web Search for: {keyword}")

    # Approach 1: Check if Responses API exists (Users docs mentioned it)
    if hasattr(client, 'responses'):
        print("[Approach 1] Using client.responses endpoint...")
        try:
            # Need to figure out the method, assuming client.responses.create
            response = await client.responses.create(
                model="gpt-4o-mini-search-preview",
                tools=[{"type": "web_search"}],
                input=f"Analyze '{keyword}' and explain why it is popular.",
            )
            print("\n[Response Success - Responses API]")
            print(response.output_text)
            return
        except Exception as e:
            print(f"[Approach 1 Failed] {e}")
    else:
        print("[Approach 1] client.responses NOT found in this library version.")

    # Approach 2: Chat Completions WITHOUT explicit tools (Maybe model handles it?)
    print("\n[Approach 2] Using Chat Completions WITHOUT 'web_search' tool (Implicit)...")
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini-search-preview", 
            messages=[
                {"role": "system", "content": "You are a trend analyzer. Please SEARCH the web online to explain the keyword."},
                {"role": "user", "content": f"Search and analyze '{keyword}'"}
            ]
        )
        print("\n[Response Success - Implicit]")
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"[Approach 2 Failed] {e}")

if __name__ == "__main__":
    asyncio.run(test_native_search())
