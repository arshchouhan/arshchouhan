import requests
import os

font_url = "https://github.com/JetBrains/JetBrainsMono/raw/master/fonts/ttf/JetBrainsMono-Bold.ttf"
font_path = "scripts/JetBrainsMono-Bold.ttf"

if not os.path.exists(font_path):
    print(f"Downloading font from {font_url}...")
    response = requests.get(font_url)
    with open(font_path, "wb") as f:
        f.write(response.content)
    print("Font downloaded.")
else:
    print("Font already exists.")
