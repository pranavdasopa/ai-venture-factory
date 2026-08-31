from app.models.ollama import OllamaModel


model = OllamaModel()

print("=" * 50)
print("LOCAL AI TEST")
print("=" * 50)

answer = model.generate(
    system_prompt="You are a concise business analyst.",
    user_prompt="Give exactly three short reasons why customer validation is important.",
)

print(answer)