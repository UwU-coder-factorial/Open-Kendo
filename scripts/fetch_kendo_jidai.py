import urllib.request
import re
from bs4 import BeautifulSoup

url = "https://kendojidai.com/2024/08/12/how-to-create-an-ideal-kamae-koda-kunihide/"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
try:
    html = urllib.request.urlopen(req).read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    article = soup.find("article") or soup
    imgs = article.find_all("img")
    print(f"Total img tags: {len(imgs)}")
    for img in imgs:
        src = img.get("src") or img.get("data-src")
        alt = img.get("alt", "")
        print(f"SRC: {src} | ALT: {alt}")
except Exception as e:
    print(f"Error: {e}")
