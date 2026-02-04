import time
from typing import List, Dict

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"
START_URL = f"{BASE_URL}/"


def fetch_page(url: str) -> BeautifulSoup:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def parse_quotes(soup: BeautifulSoup) -> List[Dict[str, str]]:
    quotes_data = []
    for quote in soup.select(".quote"):
        text = quote.select_one(".text")
        author = quote.select_one(".author")
        tags = [tag.get_text(strip=True) for tag in quote.select(".tags .tag")]
        quotes_data.append(
            {
                "text": text.get_text(strip=True) if text else "",
                "author": author.get_text(strip=True) if author else "",
                "tags": ", ".join(tags),
            }
        )
    return quotes_data


def find_next_page(soup: BeautifulSoup) -> str | None:
    next_link = soup.select_one("li.next > a")
    if not next_link:
        return None
    href = next_link.get("href")
    return f"{BASE_URL}{href}" if href else None


def scrape_all_quotes() -> List[Dict[str, str]]:
    all_quotes = []
    next_url = START_URL
    while next_url:
        soup = fetch_page(next_url)
        all_quotes.extend(parse_quotes(soup))
        next_url = find_next_page(soup)
        time.sleep(0.2)
    return all_quotes


def main() -> None:
    quotes = scrape_all_quotes()
    if not quotes:
        raise SystemExit("No quotes found.")

    df = pd.DataFrame(quotes)
    output_file = "quotes.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Saved {len(df)} quotes to {output_file}")


if __name__ == "__main__":
    main()
