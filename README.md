# Reverse Image Search API

RIS is as an API which uses beautiful soup to scrape data from google image search results.   

### Installation Guide

* Fork this repository
* Clone the forked repository - `git clone https://github.com/{username}/ris-api.git`
* change directory - `cd ris-api`
* Install the required libraries - `pip install -r requirements.txt`
* Run the application - `python server.py`
* Send a POST Request to http://localhost:5000/search using   
    `curl -d '{"image_url":"image link"}' -H "Content-Type: application/json" -X POST http://localhost:5000/search`
* You can also send a POST request to http://localhost:5000/labelsearch perform a google text search using  
    `curl -d '{"q":"keyword"}' -H "Content-Type: application/json" -X POST http://localhost:5000/labelsearch`