from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests


app = FastAPI()

def crawl_dantri(url: str):
    soup = BeautifulSoup(requests.get(url).content, features='lxml')
    wrap = soup.find('div', class_='singular-wrap')
    if not wrap:
        return {}

    title = wrap.find('h1', class_='title-page detail')

    author_name = wrap.find('div', class_='author-name')
    author_time = wrap.find('time', class_='author-time')

    author = {
        'name': None if not author_name else author_name.text.strip(),
        'time': None if not author_time else author_time.text.strip()
    }

    sapo = wrap.find('h2',class_='singular-sapo')

    content = wrap.find('div',class_='singular-content')
    if content:
        ps = '\n'.join([p.text.strip() for p in content.find_all('p', recursive=False)])
        images = [{
            'src': fig.find('img')['data-original'],
            'caption': fig.find('figcaption').text.strip()
        } for fig in content.find_all('figure')]
    else:
        ps = ""
        images = []

    source = wrap.find('div',class_='singular-source')

    return {
        'title': None if not title else title.text.strip(),
        'author': author,
        'sapo': None if not sapo else sapo.text.strip(),
        'content': ps,
        'images': images,
        'source': None if not source else source.text.strip()
    }

def check_url(url: str):
    try:
        result = urlparse(url)
        if all([result.scheme, result.netloc]):
            if result.netloc.startswith("dantri"):
                return "dantri"
    except:
        return None

class Item(BaseModel):
    url: str

@app.post("/crawl/")
async def crawl(item: Item):
    if check_url(item.url) == 'dantri':
        return JSONResponse(jsonable_encoder(crawl_dantri(item.url)))
    else:
        return {}