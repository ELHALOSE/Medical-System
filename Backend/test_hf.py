import os
from huggingface_hub import InferenceClient

print("TOKEN:", repr(os.getenv("HF_TOKEN")))

client = InferenceClient(token=os.getenv("HF_TOKEN"))
response = client.chat_completion(
    model="Qwen/Qwen2.5-7B-Instruct",
    messages=[{"role": "user", "content": "hello"}],
    max_tokens=20,
)
print(response.choices[0].message.content)
