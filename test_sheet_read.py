import pandas as pd

sheet_id = "1yBnfIni5qAjMM0_g90oxR2jXTgUlI98oaRz7Kz0g4sg"

url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

df = pd.read_csv(url)

print("Google Sheet data loaded successfully!")
print(df.head())
