"""Сервис фонового сбора отзывов с сервиса Otzovik.

Лабораторная работа №5 по курсу «Новые технологии в РПС».
Выполнил: студент Кондратенко А.С. (гр. M_PIN_RIS_2607)
"""

from __future__ import annotations

from pathlib import Path
import random
import re
import time
from typing import Dict, Set

import requests
from bs4 import BeautifulSoup


def scrape_reviews_batch(
    object_slug: str = "sberbank_rossii",
    base_dir: str = "dataset",
    target_count: int = 10,
    max_pages: int = 5,
) -> Dict[int, int]:
    """Выполняет сбор отзывов по страницам пагинации."""
    root = Path(base_dir)
    root.mkdir(parents=True, exist_ok=True)
    counts = {star: 0 for star in range(1, 6)}
    seen_ids: Set[str] = set()

    for star in range(1, 6):
        folder = root / str(star)
        folder.mkdir(parents=True, exist_ok=True)
        counts[star] = len(list(folder.glob("*.txt")))

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0",
        "Accept-Language": "ru-RU,ru;q=0.9",
        "Referer": "https://otzovik.com/",
    })

    base_url = "https://otzovik.com"
    for page in range(1, max_pages + 1):
        if all(counts[s] >= target_count for s in range(1, 6)):
            break

        url = (
            f"{base_url}/reviews/{object_slug}/"
            if page == 1
            else f"{base_url}/reviews/{object_slug}/{page}/"
        )

        try:
            resp = session.get(url, timeout=5)
            if resp.status_code != 200:
                break
            soup = BeautifulSoup(resp.text, "lxml")
        except requests.RequestException:
            break

        for link in soup.find_all("a", href=re.compile(r"/review_\d+\.html")):
            href = link.get("href", "")
            id_m = re.search(r"/review_(\d+)\.html", href)
            if not id_m or id_m.group(1) in seen_ids:
                continue

            rev_id = id_m.group(1)
            card = link.find_parent(
                "div", class_=lambda c: c and "item" in c.split()
            ) or link.find_parent("div")
            if not card:
                continue

            score_tag = card.find(
                attrs={"title": re.compile(r"Общий рейтинг:\s*(\d+)")}
            )
            if not score_tag:
                continue

            r_match = re.search(r"Общий рейтинг:\s*(\d+)", score_tag["title"])
            if not r_match:
                continue
            rating = int(r_match.group(1))

            if rating not in counts or counts[rating] >= target_count:
                continue

            title = link.get_text(strip=True)
            body_el = card.find(class_=re.compile(r"review-body|description"))
            text = body_el.get_text(" ", strip=True) if body_el else title

            filename = f"{str(counts[rating]).zfill(4)}.txt"
            (root / str(rating) / filename).write_text(
                f"{title}\n\n{text}\n", encoding="utf-8"
            )
            seen_ids.add(rev_id)
            counts[rating] += 1

        time.sleep(random.uniform(1.0, 2.0))

    return counts
