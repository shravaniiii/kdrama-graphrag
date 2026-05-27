import requests
from bs4 import BeautifulSoup
import time
import json
import os

HEADERS = {'User-Agent': 'Mozilla/5.0'}

def scrape_drama(title: str):
    url_title = title.replace(' ', '_').replace(':', '')
    url = f'https://asianwiki.com/{url_title}'
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Title
        h1 = soup.find('h1')
        drama_title = h1.text.strip() if h1 else title
        
        # Synopsis
        synopsis = ""
        syn_header = soup.find('span', {'id': 'Plot_Synopsis_by_AsianWiki_Staff_.C2.A9'})
        if syn_header:
            p = syn_header.find_next('p')
            if p:
                synopsis = p.text.strip()
        
        # Cast
        cast = []
        cast_header = soup.find('span', {'id': 'Cast'})
        if cast_header:
            ul = cast_header.find_next('ul')
            if ul:
                cast = [li.text.strip().split(' - ')[0] for li in ul.find_all('li')][:10]
        
        return {
            'title': drama_title,
            'synopsis': synopsis,
            'cast': cast,
            'url': url
        }
    except Exception as e:
        print(f"Error scraping {title}: {e}")
        return None

# List of dramas to scrape
dramas = [
    'Goblin', 'Crash_Landing_on_You', 'Vincenzo',
    'Squid_Game', 'Extraordinary_Attorney_Woo',
    'The_Glory', 'My_Mister', 'Signal',
    'Reply_1988', 'Hospital_Playlist'
]

results = []
for drama in dramas:
    print(f'Scraping {drama}...')
    data = scrape_drama(drama)
    if data:
        results.append(data)
        print(f"  ✓ Got synopsis: {data['synopsis'][:80]}...")
    time.sleep(2)  # be polite

# Save results
os.makedirs('data_raw', exist_ok=True)
with open('data_raw/asianwiki_data.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f'\nDone! Scraped {len(results)} dramas')
print('Saved to data_raw/asianwiki_data.json')