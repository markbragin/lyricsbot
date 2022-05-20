import sys
from typing import Optional
import re

import requests
from bs4 import BeautifulSoup


def _get_google_url(songname: str) -> Optional[str]:
    search_url = "https://google.com/search?"
    search_params = {"q": "+".join(songname.split() + ["lyrics"])}
    google_res = requests.get(search_url, search_params)
    if google_res.status_code != 200:
        return None

    search_page = BeautifulSoup(google_res.text, 'lxml')
    a_tag = search_page.find("a", {"href": re.compile("https://genius.com.")})
    return a_tag["href"] if a_tag else None  # type: ignore


def _parse_genius_page(gurl: str) -> Optional[str]:
    genius_res = requests.get(f"https://google.com{gurl}")
    if genius_res.status_code != 200:
        return None

    genius_page = BeautifulSoup(genius_res.text.replace("<br/>", '\n'), 'lxml')

    text = ""

    lyrics = _get_lyrics(genius_page)
    if not lyrics:
        return None

    title = _get_title(genius_page)
    if title:
        text += title + "\n\n"

    text += lyrics
    text += f"\n\nSource: {genius_res.url}"
    return text


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
    lyrics_containers = genius_page.find_all("div",
                                             {"data-lyrics-container": "true"})
    for container in lyrics_containers:
        lyrics += container.get_text() + '\n'
    return lyrics if lyrics else None


def get_formatted_lyrics(songname: str) -> Optional[str]:
    gurl = _get_google_url(songname)
    if not gurl:
        return None

    text = _parse_genius_page(gurl)
    return text if text else None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(get_formatted_lyrics(" ".join(sys.argv[1:])))
    else:
        print("Pass song name as argument in cli")
