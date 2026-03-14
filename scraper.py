"""
Çanakkale Belediyesi otobüs saatleri PDF linklerini çeken scraper.
Bağımlılıklar: requests, beautifulsoup4
Çıktı: data/links.json
"""

import json
import os
import re
import requests
from bs4 import BeautifulSoup

URL = "https://ulasim.canakkale.bel.tr/rehber/hatlar-otobus-saatleri/"

CATEGORY_KEYWORDS = {
    "haftaici": ["hafta i", "haftai", "weekday"],
    "haftasonu": ["hafta s", "haftason", "weekend"],
    "arefe": ["arefe"],
    "bayram": ["bayram"],
}


def categorize(text: str) -> str:
    """PDF bağlantı metnini kategoriye göre eşleştirir."""
    lower = text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in lower:
                return category
    return "diger"


def scrape() -> dict:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(URL, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    result = {
        "haftaici": [],
        "haftasonu": [],
        "arefe": [],
        "bayram": [],
        "diger": [],
    }

    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        if not href.lower().endswith(".pdf"):
            continue

        # Tam URL yap
        if href.startswith("//"):
            href = "https:" + href
        elif href.startswith("/"):
            href = "https://ulasim.canakkale.bel.tr" + href

        link_text = tag.get_text(separator=" ", strip=True)
        if not link_text:
            # href'ten dosya adı al
            link_text = os.path.basename(href)

        category = categorize(link_text)
        # Aynı linki tekrar ekleme
        existing_urls = [item["url"] for item in result[category]]
        if href not in existing_urls:
            result[category].append({"label": link_text, "url": href})

    return result


def main():
    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", "links.json")

    new_data = scrape()

    # Değişiklik kontrolü
    old_data = {}
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            old_data = json.load(f)

    if new_data == old_data:
        print("Değişiklik yok, dosya güncellenmedi.")
        return

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    print(f"data/links.json güncellendi: {sum(len(v) for v in new_data.values())} link bulundu.")


if __name__ == "__main__":
    main()
