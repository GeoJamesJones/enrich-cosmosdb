import requests
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image
from io import BytesIO
import json

def assert_cv_key(cv_key):
    cv_subscription_key = cv_key
    assert cv_subscription_key
    return cv_subscription_key

def ocr_image(subscription_key, image_url, services_url, json_list):
    headers = {'Ocp-Apim-Subscription-Key': subscription_key}
    params  = {'language': 'unk', 'detectOrientation': 'true'}
    data    = {'url': image_url}
    response = requests.post(services_url, headers=headers, params=params, json=data)
    response.raise_for_status()
    analysis = response.json()
    json_list.append(analysis)

class Azure_Text:
    """This will eventually get filled in"""
    
    def __init__(self, subscription_key, azure_api_url):
        """Docstring"""
        self.subcription_key = subscription_key
        self.azure_api_url = azure_api_url
        self.language_api_url = azure_api_url + "/languages"
        self.sentiment_api_url = azure_api_url + "/sentiment"
        self.key_phrase_api_url = azure_api_url + "/keyPhrases"
        self.entity_linking_api_url = azure_api_url + "/entities"
        
    def detect_language(self, input_text_string):
        """Docstring"""
        language_dict = {}
        
        documents = { 'documents': [
            { 'id': '1', 'text': input_text_string }
        ]}
        
        headers   = {"Ocp-Apim-Subscription-Key": self.subcription_key}
        response  = requests.post(self.language_api_url, headers=headers, json=documents)
        languages = response.json()
        

        for item in languages['documents']:
            item_id = item['id']
            item_content = item['detectedLanguages']
            language_dict[item_id] = item_content
            
        try:
            return language_dict['1'][0]['iso6391Name']
        except:
            return 'Unspecified error:  Text was not successfully processed.' 
    
    def named_entity_recognition(self, input_text_string):
        """Docstring"""
        entity_dict = {}
        
        documents = {'documents' : [
          {'id': '1', 'text': input_text_string}
        ]}
    
        headers   = {"Ocp-Apim-Subscription-Key": self.subcription_key}
        response  = requests.post(self.entity_linking_api_url, headers=headers, json=documents)
    
        entities = response.json()
    

        for objects in entities['documents']:
            entity_count = 0
            for entity in objects['entities']:
                entity_id = objects['id'] + "-" + str(entity_count)
                entity_dict[entity_id] = entity
                entity_count +=1
        
        try:
            return entity_dict
        except:
            return 'Unspecified error:  Text was not successfully processed.'
    
    def analyze_sentiment(self, input_text_string):
        """Docstring"""
        
        laguage = self.detect_language(input_text_string) 
        documents = {'documents' : [
            {'id': '1', 'language': laguage, 'text': input_text_string},
        ]}
        
        headers   = {"Ocp-Apim-Subscription-Key": self.subcription_key}
        response  = requests.post(self.sentiment_api_url, headers=headers, json=documents)
        sentiments = response.json()['documents'][0]['score']
        
        try:
            return sentiments
        except:
            return 'Unspecified error:  Text was not successfully processed.'

class NER_Entity:
    """Fill me in"""
    
    def __init__(self, ner_key, ner_value):
        self.entity_id = ner_key
        self.name = ner_value['name']
        if 'wikipediaLanguage' in ner_value.keys():
            self.language = ner_value['wikipediaLanguage']
        if 'wikipediaId' in ner_value.keys():
            self.wikipedia_id = ner_value['wikipediaId']
        if 'wikipediaUrl' in ner_value.keys():
            self.wikipedia_url = ner_value['wikipediaUrl']
        if 'bingId' in ner_value.keys():
            self.bing_id = ner_value['bingId']
        if 'type' in ner_value.keys():
            self.type = ner_value['type']
            if ner_value['type'] == 'Location':
                self.spatial_entity = True
                coordinates = self.geocode_address()
                self.x = coordinates['x']
                self.y = coordinates['y']
            else:
                self.spatial_entity = False
        else:
            self.spatial_entity = False
        
        if 'subType' in ner_value.keys():
            self.sub_type = ner_value['subType']
            
    def geocode_address(self):
        """Use World Geocoder to get XY for one address at a time."""
        querystring = {
                "f": "json",
                "singleLine": self.name}
        url = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"  # noqa: E501
        response = requests.request("GET", url, params=querystring)
        p = response.text
        j = json.loads(p)
        location = j['candidates'][0]['location']  # returns first location as X, Y
        return location
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
    def post_to_geoevent(self, geoevent_url):
        headers = {
            'Content-Type': 'application/json',
                }

        response = requests.post((geoevent_url), headers=headers, data=self.toJSON())