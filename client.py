from dataclasses import dataclass
import re
import sys
import time
from typing import Optional

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests


UA = UserAgent()

RETRIES = 2
SLEEP_TIME = 0.2


@dataclass
class Source:
    html: str
    url: str


def _get_first_genius_gurl(songname: str) -> Optional[str]:
    search_url = "https://google.com/search?"
    search_params = {"q": "+".join(songname.split() + ["lyrics"])}

    response = None
    tries = 0
    while response is None and tries <= RETRIES:
        tries += 1
        headers = {"UserAgent": UA.random}
        response = requests.get(search_url, search_params, headers=headers)
        if response.status_code != 200:
            time.sleep(SLEEP_TIME)

    if response == None or response.status_code != 200:
        return None

    search_page = BeautifulSoup(response.text, "lxml")
    a_tag = search_page.find("a", {"href": re.compile("https://genius.com")})
    return a_tag["href"] if a_tag else None  # type: ignore


def _get_genius_page(gurl: str) -> Optional[Source]:
    response = None
    tries = 0
    while response is None and tries <= RETRIES:
        tries += 1
        headers = {"UserAgent": UA.random}
        response = requests.get(f"https://google.com{gurl}", headers=headers)
        if response.status_code != 200:
            time.sleep(SLEEP_TIME)

    if response == None or response.status_code != 200:
        return None

    source = Source(response.text.replace("<br/>", "\n"), response.url)
    return source


def _get_title(genius_page: BeautifulSoup) -> Optional[str]:
    name_tag = genius_page.find("h1", {"class": re.compile("SongHeader")})
    if name_tag:
        name = name_tag.get_text()
        artists_tag = name_tag.parent.a  # type: ignore
        if artists_tag:
            artists = artists_tag.get_text()
            return f"{name} - {artists}"
    return None


def _get_lyrics(genius_page: BeautifulSoup) -> Optional[str]:
    lyrics = ""
    lyrics_containers = genius_page.find_all(
        "div", {"data-lyrics-container": "true"}
    )
    for container in lyrics_containers:
        lyrics += container.get_text() + "\n"
    return lyrics if lyrics else None


def get_formatted_answer(songname: str) -> Optional[str]:
    genius_url = _get_first_genius_gurl(songname)
    if not genius_url:
        return None

    genius_page = _get_genius_page(genius_url)
    if not genius_page:
        return None

    genius_soup = BeautifulSoup(genius_page.html, "lxml")

    lyrics = _get_lyrics(genius_soup)
    if not lyrics:
        return None

    title = _get_title(genius_soup)
    title = "? - ?" if not title else title

    return f"{title}\n\n{lyrics}\n\nSource: {genius_page.url}"


if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = get_formatted_answer(" ".join(sys.argv[1:]))
        if text:
            print(text)
        else:
            print("Not found")
    else:
        print("ERROR: Pass song name as argument\n")
