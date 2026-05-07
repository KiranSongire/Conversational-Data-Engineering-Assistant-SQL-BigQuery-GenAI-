import google.generativeai as genai

genai.configure(api_key="AIzaSyBsfvz4EqgftsKqhriSS5RCSBGUaTQv9Ro")

model = genai.GenerativeModel("gemini-flash-lite-latest")

response = model.generate_content("Hello")

print(response.text)