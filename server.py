import os
import sys
import argparse
import requests
import webbrowser
import json
import shutil
from urllib.parse import quote
import pycurl
import json
from flask import Flask, url_for, jsonify, request
python3 = False
try:
    from StringIO import StringIO
except ImportError:
    python3 = True
    import io as bytesIOModule
from bs4 import BeautifulSoup
if python3:
    import certifi


SEARCH_LABEL = 'https://www.google.com/search?q='
app = Flask(__name__)

@app.route('/labelsearch', methods = ['POST'])
def label_search():
    if request.headers['Content-Type'] != 'application/json':
        return "Request must be JSON format"
    client_json = json.dumps(request.json)
    client_data = json.loads(client_json)

    code = doImageSearch(SEARCH_LABEL + quote(client_data['q']))
    
    return parseLabelResults(code)

@app.route('/search', methods = ['POST'])
def search():
    if request.headers['Content-Type'] != 'application/json':
        return "Requests must be in JSON format. Please make sure the header is 'application/json' and the JSON is valid."
    client_json = json.dumps(request.json)
    client_data = json.loads(client_json)

    saveImage(client_data['image_url'])
    dirname= os.path.dirname(os.path.abspath(__file__))
    filename= os.path.join(dirname,'example.jpg')
    searchUrl='https://www.google.hr/searchbyimage/upload'
    multipart={'encoded_image':(filename, open(filename,'rb')),'image_content':''}
    response=requests.post(searchUrl, files=multipart, allow_redirects=False)
    fetchUrl=response.headers['Location']
    code = doImageSearch(fetchUrl)
    return parseResults(code)

def saveImage(image_url, image_path = "./example.jpg"):
    success = False

    os.makedirs(os.path.dirname(os.path.abspath(image_path)), exist_ok=True)

    r = requests.get(image_url, stream=True)
    if r.status_code == 200:
        with open(image_path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
            success = True

    return success

def doImageSearch(full_url):
    # Directly passing full_url
    """Return the HTML page response."""

    if python3:
        returned_code = bytesIOModule.BytesIO()
    else:
        returned_code = StringIO()
    # full_url = SEARCH_URL + image_url

    if app.debug:
        print('POST: ' + full_url)

    conn = pycurl.Curl()
    if python3:
        conn.setopt(conn.CAINFO, certifi.where())
    conn.setopt(conn.URL, str(full_url))
    conn.setopt(conn.FOLLOWLOCATION, 1)
    conn.setopt(conn.USERAGENT, 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0')
    conn.setopt(conn.WRITEFUNCTION, returned_code.write)
    conn.perform()
    conn.close()
    if python3:
        return returned_code.getvalue().decode('UTF-8')
    else:
        return returned_code.getvalue()

def parseLabelResults(code):
    soup = BeautifulSoup(code, 'html.parser')
    label_results = {
        'links': [],
        'titles': [],
        'maps': '',
        'images': [],
        'sources':[],
        'shop':[],
        'buy_link':[]
    }

    for div in soup.findAll('div', attrs={'class':'rc'}):
        sLink = div.find('a')
        label_results['links'].append(sLink['href'])

    for buy in soup.findAll('div', attrs={'class':'mnr-c pla-unit'}):
        if type(buy)!='NoneType':
            blink=buy.find('a').find_next_sibling('a')
            if type(blink)!='NoneType':
                label_results['buy_link'].append(blink['href'])

    for title in soup.findAll('div', attrs={'class':'rc'}):
        title_name=title.find('h3')
        label_results['titles'].append(title_name.get_text())

    for shopping in soup.findAll('div', attrs={'class':'hdtb-mitem hdtb-imb'}):
        if type(shopping)!='NoneType':
            if shopping.find('a').contents[0]=='Shopping':
                a=shopping.find('a')
                label_results['shop'].append('https://www.google.com' + a['href'])

    for map_link in soup.findAll('div', attrs={'class':'xERobd'}):
        if type(map_link)!='NoneType':
            mlink=map_link.find('a')
            if type(mlink)!='NoneType':
                label_results['maps']='https://www.google.com' + mlink['href']

    for image in soup.findAll('div', attrs={'id':'imagebox_bigimages'}):
        if type(image)!='NoneType':
            image_link=image.find('a')
            if type(image_link)!='NoneType':
                label_results['images'].append('https://www.google.com'+image_link['href'])

    for image in soup.findAll('div', attrs={'class':'PFaeqe'}):
        if type(image)!='NoneType':
            image_link=image.find('a')
            if type(image_link)!='NoneType':
                label_results['images'].append('https://www.google.com'+image_link['href'])

    imgcode=doImageSearch(label_results['images'][0])
    imgsoup = BeautifulSoup(imgcode, 'html.parser')
    for a in imgsoup.findAll('a', attrs={'class':'rg_l'}):
        if type(a) != 'NoneType':
            img=a.find('img', attrs={'class':'rg_ic rg_i'})
            if type(img)!='NoneType':
                attrslist=img.attrs
                for k in attrslist:
                    if k=='data-src':
                        label_results['sources'].append(attrslist[k])
    print(label_results)
    sys.stdout.flush()
    print("Successful search")

    return json.dumps(label_results)

def parseResults(code):
    """Parse/Scrape the HTML code for the info we want."""

    soup = BeautifulSoup(code, 'html.parser')

    results = {
        'links': [],
        'descriptions': [],
        'titles': [],
        'similar_images': [],
        'sources':[],
        'shop':[],
        'best_guess': ''
    }

    for div in soup.findAll('div', attrs={'class':'rc'}):
        sLink = div.find('a')
        results['links'].append(sLink['href'])

    for desc in soup.findAll('span', attrs={'class':'st'}):
        results['descriptions'].append(desc.get_text())

    for title in soup.findAll('div', attrs={'class':'rc'}):
        title_name=title.find('h3')
        results['titles'].append(title_name.get_text())

    for shopping in soup.findAll('div', attrs={'class':'hdtb-mitem hdtb-imb'}):
        if type(shopping)!='NoneType':
            if shopping.find('a').contents[0]=='Shopping':
                a=shopping.find('a')
                results['shop'].append('https://www.google.com' + a['href'])

    for best_guess in soup.findAll('a', attrs={'class':'fKDtNb'}):
      results['best_guess'] = best_guess.get_text()

    for image in soup.findAll('div', attrs={'id':'imagebox_bigimages'}):
        if type(image)!='NoneType':
            image_link=image.find('a')
            if type(image_link)!='NoneType':
                results['similar_images'].append('https://www.google.com'+image_link['href'])
     

    imgcode=doImageSearch(results['similar_images'][0])
    imgsoup = BeautifulSoup(imgcode, 'html.parser')
    for a in imgsoup.findAll('a', attrs={'class':'rg_l'}):
        if type(a) != 'NoneType':
            img=a.find('img', attrs={'class':'rg_ic rg_i'})
            if type(img)!='NoneType':
                attrslist=img.attrs
                for k in attrslist:
                    if k=='data-src':
                        results['sources'].append(attrslist[k])

    print(results)
    sys.stdout.flush()
    print("Successful search")

    return json.dumps(results)



def main():
    parser = argparse.ArgumentParser(description='Meta Reverse Image Search API')
    parser.add_argument('-p', '--port', type=int, default=5000, help='port number')
    #parser.add_argument('-d','--debug', action='store_true', help='enable debug mode')
    #parser.add_argument('-c','--cors', action='store_true', default=False, help="enable cross-origin requests")
    args = parser.parse_args()

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()
