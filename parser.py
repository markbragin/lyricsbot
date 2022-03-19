from typing import Dict, Optional
import re

import requests
from bs4 import BeautifulSoup


def get_lyrics(songname: str) -> Optional[str]:
    search_url = "https://google.com/search?"
    search_params = {"q": "+".join(songname.split() + ["genius.com"])}

    google_res = requests.get(search_url, search_params)
    if google_res.status_code != 200:
        return None

    search_page = BeautifulSoup(google_res.text, 'lxml')

    a_tag = search_page.find("a", {"href": re.compile("https://genius.com.")})
    if not a_tag:
        return None
    first_qlink = a_tag["href"]  # type: ignore

    genius_res = requests.get(f"https://google.com{first_qlink}")
    if genius_res.status_code != 200:
        return None

    genius_page = BeautifulSoup(genius_res.text.replace("<br/>", '\n'), 'lxml')
    lyrics_containers = genius_page.find_all("div",
            {"data-lyrics-container": "true"})

    text = ""
    for container in lyrics_containers:
        text += container.get_text() + '\n'

    return text if text else None


if __name__ == "__main__":
    print(get_lyrics("kendrik lama dna"))
