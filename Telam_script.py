import requests
import urllib.request
import time
from bs4 import BeautifulSoup
from html.parser import HTMLParser
import re
import json

def get_page(url):
  response = requests.get(url)
  return response

def get_links(response):
  links = []
  soup = BeautifulSoup(response.text, 'html.parser')
  for link in soup.find_all('a'):
    links.append(link.get('href'))
  return links

def get_id(link):
  print(link)
  return link.split("/")[2]

def next_page(url):
  l = url.split("/")
  return (l[len(l)-1])

def make_dictionary(response):
  soup = BeautifulSoup(response.text, 'html.parser')
  f = soup.p
  etiquetas = f.find_next('strong')
  localizacion = etiquetas.find_next('strong') 
  isdate = re.compile('\d{2}/\d{2}/\d{4} \d{2}:\d{2}')
  noticia = {}
  noticia['etiquetas'] = []
  i = 0
  while etiquetas.find_next('p').string != 'ABRIR':
    i += 1
    for s in etiquetas.find_next('p').stripped_strings:
      if s[-1] == '-':
        noticia['etiquetas'].append(s[:len(s)-2])
      elif s[-1] == ':':
        pass
      else:
        noticia['etiquetas'].append(s)
    etiquetas = etiquetas.find_next('p')


  while f is not None:
    if f.string != None:

      if isdate.match(f.string) is not None:
        noticia['fecha'] = f.string
        noticia['temas'] = f.find_next('p').string

      if 'Categoría:' in f.contents[0]:
        noticia['categoria'] = f.find_next('p').string

      if 'class' in f.attrs and f.attrs['class'][0] == 'title':
        noticia['titulo'] = f.string
        for s in f.find_next('div').stripped_strings:
          if s =='Ver más':
            pass
          else:
            noticia['resumen'] = s

    f = f.find_next('p')
  return noticia

def get_dataset(amount= 1,prev_dict= {}):
  count = 0
  url = 'https://cablera.telam.com.ar/cables'
  dataset=prev_dict
  for j in range(amount):
    response = get_page(url)
    inext = next_page(url)
    if not inext=="cables":
      inext = int(inext)
    else:
      inext = 0
    links = get_links(response)
    del links[:33]
    del links[-24:]
    url = links[len(links)-1]
    if inext > 7:
      del links[-16:]
    else:
      del links[-(8+inext):]
    print(inext,url)
    i=0
    for link in links:
      i=i+1
      id = get_id(link)
      if id in prev_dict:
        count += 1
        if count >= 10:
          return dataset
        else:
          pass
      else:
        print(i,link)
        response = get_page('https://cablera.telam.com.ar' + link)
        noticia = make_dictionary(response)
        print(noticia)
        dataset[id] = noticia
        time.sleep(1)
  return dataset

def main():
    with open("news_2022",'r') as fp:
        news = fp.read()
    news = json.loads(news)

    news = get_dataset(20, prev_dict = news)

    with open('news_2022', 'w') as fp:
        json.dump(news, fp)

    import pandas as pd
    df = pd.DataFrame(news)
    final = df.T
    final.index.name = "id"
    final.to_csv('news.csv', index=True)
    print(len(news))

main()
