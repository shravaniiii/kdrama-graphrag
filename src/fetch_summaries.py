import pandas as pd
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

df = pd.read_csv('data_raw/kdrama.csv')
os.makedirs('graphrag_input/input', exist_ok=True)

def get_wikipedia_summary(drama_name):
    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + \
          drama_name.replace(" ", "_") + "_(TV_series)"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json().get('extract', '')
    except:
        pass
    return ""

for _, row in df.iterrows():
    summary = get_wikipedia_summary(row['Name'])
    time.sleep(1)

    content = f"""Title: {row['Name']}
Year: {row['Year']}
Rating: {row['Rating']}
Episodes: {row['Episodes']}
Aired On: {row['Aired On']}
Genres: {row['Genres']}
Tags: {row['Tags']}
Main Actors: {row['Main Actors']}

Plot Summary:
{summary if summary else "Summary not available."}
"""

    filename = f"graphrag_input/input/{row['Name'].replace(' ', '_').replace('/', '_').replace(',', '')}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ {row['Name']}")

print(f"\nDone! Created {len(df)} files.")