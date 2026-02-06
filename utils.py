from openai import OpenAI

# Call LLM But It does not have previous context
def call_llm(message):
    client = OpenAI(base_url = "http://localhost:11434/v1", api_key="123")
    resp = client.chat.completions.create(
        model = "qwen3:4b-instruct-2507-q4_K_M",
        messages=[{"role": "user", "content": message}],
        temperature = 0
    )
    return resp.choices[0].message.content


if __name__ == "__main__":
    print(call_llm("Hey, How are you?"))
