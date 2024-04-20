from openai import OpenAI

client = OpenAI(
    api_key='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'
)

stream = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello, can you tell me what is yield in python?"}],
    stream=True,
)
for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="")