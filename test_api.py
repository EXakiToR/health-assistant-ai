from openai import OpenAI

client = OpenAI(
  api_key="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"
)

response = client.responses.create(
  model="gpt-5-nano",
  input="write a haiku about ai",
  store=True,
)

print(response.output_text);
