from fastapi import FastAPI
# from fastapi.responses import PlainTextResponse
from fastapi.responses import StreamingResponse
from groq import Groq
import os 

app = FastAPI()

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
def idea():
    client = Groq()
    prompt = [{"role": "user", "content": "Reply with a new business idea for AI Agents, formatted with headings, sub-headings and bullet points"}]

    stream = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=prompt,
        stream=True
    )

    def event_stream():
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                for line in delta.split("\n"):
                    yield f"data: {line}\n"
                yield "\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream"
    )