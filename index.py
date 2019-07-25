import requests
import os
from flask import Flask, Response, __version__

IMMO_SEARCH_URL = 'https://www.immobilienscout24.de/Suche/S-2/Wohnung-Miete/Polygonsuche/%7B_r_IsyqpAmJap@%7Bb@yv@gb@cAsPyJqc@%7Bw@uJ_iA%7C%7C@yiEr_A_iArp@%7BfAnTkp@bj@mTniAxJpPmDhQnTtNtcA%7Cq@ooA%7DBnr@lZ%7CgAzf@eBtNdkAeDb%7C@%7BWf%7D@qTjSwYlEcY~wAmm@j%7CA_aAbyAoc@lEm%5CdPaj@iC/1,00-/-/EURO--700,00/-/-/false?enteredFrom=result_list#/'
DB_BUCKET = os.environ['DB_BUCKET']
DB_KEY = 'seen_apartments'
DB_AUTH_KEY = os.environ['DB_AUTH_KEY']
NOTIFICATION_URL = 'https://api.pushbullet.com/v2/pushes'
NOTIFICATION_AUTH_KEY = os.environ['NOTIFICATION_AUTH_KEY']

app = Flask(__name__)

@app.route('/findplaces')
def find_new_places():
    seen_apartments = requests.get(f'https://kvdb.io/{DB_BUCKET}/{DB_KEY}', auth=(DB_AUTH_KEY, '')).json()

    apartments = requests.post(IMMO_SEARCH_URL).json()['searchResponseModel']['resultlist.resultlist']['resultlistEntries'][0]['resultlistEntry']

    unseen_apartments = []

    for apartment in apartments:
        if apartment['@id'] not in seen_apartments:
            unseen_apartments.append(apartment)
            seen_apartments.append(apartment['@id'])
    
    parsed_unseen_apartments = []

    for a in unseen_apartments:
        apartment = a['resultlist.realEstate']

        data = {
            'type': 'link',
            'title': f"New Apartment: {apartment['title']}",
            'body': f"Address: {apartment['address']['description']}\nSize: {apartment['livingSpace']}\nPrice (warm): {apartment['calculatedPrice']['value']} EUR",
            'url': f"https://www.immobilienscout24.de/expose/{a['@id']}"
        }

        parsed_unseen_apartments.append(data)

        requests.post(NOTIFICATION_URL, headers={'Access-Token': NOTIFICATION_AUTH_KEY}, json=data)

    requests.post(f'https://kvdb.io/{DB_BUCKET}/{DB_KEY}', auth=(DB_AUTH_KEY, ''), json=seen_apartments)

    return {
        'status' : 'SUCCESS',
        'unseen_apartments' : parsed_unseen_apartments
    }