from playwright.sync_api import sync_playwright
import json
import time
import os

DRAMAS = [
    "Goblin", "Crash Landing on You", "Squid Game",
    "Extraordinary Attorney Woo", "The Glory", "Vincenzo",
    "Itaewon Class", "My Mister", "Reply 1988", "Hospital Playlist"
]

def find_and_scrape(page, title):
    try:
        # Search with South Korea filter
        search_url = f"https://mydramalist.com/search?q={title.replace(' ', '+')}&type=drama&country=South+Korea"
        page.goto(search_url, timeout=30000)
        page.wait_for_load_state('networkidle', timeout=15000)

        # Get all results and pick best match
        links = page.locator('h6.title a').all()
        best_href = None
        for link in links[:3]:
            link_text = link.inner_text().lower()
            if any(word.lower() in link_text for word in title.split()):
                best_href = link.get_attribute('href')
                break

        if not best_href:
            best_href = page.locator('h6.title a').first.get_attribute('href')

        drama_url = f"https://mydramalist.com{best_href}"
        print(f"  Found URL: {drama_url}")

        # Go to drama page
        page.goto(drama_url, timeout=30000)
        page.wait_for_load_state('networkidle', timeout=15000)

        # Extract data
        drama_title = page.locator('h1').first.inner_text()

        synopsis = ""
        try:
            synopsis = page.locator('.show-synopsis').first.inner_text()
        except:
            pass

        rating = ""
        try:
            scores = page.locator('[class*="score"]').all_inner_texts()
            for s in scores:
                try:
                    val = float(s)
                    if val > 0:
                        rating = s
                        break
                except:
                    pass
        except:
            pass

        tags = []
        try:
            tags = page.locator('.show-tags a').all_inner_texts()
        except:
            pass

        return {
            "title": drama_title,
            "synopsis": synopsis,
            "rating": rating,
            "tags": tags,
            "url": drama_url
        }

    except Exception as e:
        print(f"  Error: {e}")
        return None


def scrape_all():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for title in DRAMAS:
            print(f"Scraping {title}...")
            data = find_and_scrape(page, title)
            if data:
                results.append(data)
                print(f"  ✓ Rating: {data['rating']} | Tags: {data['tags'][:3]}")
            time.sleep(3)

        browser.close()

    os.makedirs('data_raw', exist_ok=True)
    with open('data_raw/mdl_data.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nDone! Scraped {len(results)} dramas")


if __name__ == "__main__":
    scrape_all()