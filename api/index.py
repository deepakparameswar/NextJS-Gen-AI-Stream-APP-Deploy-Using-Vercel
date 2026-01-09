from fastapi import FastAPI, Depends
# from fastapi.responses import PlainTextResponse
from fastapi.responses import StreamingResponse
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials
from groq import Groq
import os 

app = FastAPI()
clerk_config = ClerkConfig(jwks_url=os.getenv("CLERK_JWKS_URL"))
clerk_guard = ClerkHTTPBearer(clerk_config)

# OLD CODE:

# @app.get("/api", response_class=PlainTextResponse)
# def idea():
#     message = """Come up with a new business idea for AI Agents. That should be correctly structured, dont add tables or somthing
# """
#     messages = [{"role": "user", "content": message}]
#     llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
#     response = "Hi"
#     try:
#         response = llm.invoke(messages)
#         print(f"<<<< invocation response >>>>: {response}")
#     except Exception as e:
#         print("Error occurred:", e)

#     return response.content


@app.get("/api", response_class=StreamingResponse)
def idea(creds: HTTPAuthorizationCredentials = Depends(clerk_guard)):
    user_id = creds.decoded["sub"]  # User ID from JWT - available for future use
    # We now know which user is making the request! 
    # You could use user_id to:
    # - Track usage per user
    # - Store generated ideas in a database
    # - Apply user-specific limits or customization
    
    client = Groq()
    prompt = [{"role": "user", "content": "Reply with a new business idea for AI Agents, formatted with headings, sub-headings and bullet points"}]

    stream = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=prompt,
        stream=True
    )

    def event_stream():
        for chunk in stream:
            text = chunk.choices[0].delta.content
            if text:
                lines = text.split("\n")
                for line in lines[:-1]:
                    yield f"data: {line}\n\n"
                    yield "data:  \n"
                yield f"data: {lines[-1]}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")