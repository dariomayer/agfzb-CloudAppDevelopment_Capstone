import requests
import json
# import related models here
from .models import CarDealer
from .models import DealerReview
from requests.auth import HTTPBasicAuth


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, api_key=None, **kwargs):
    #print(kwargs)
    #print("GET from {} ".format(url))
    try:
        # Verifica se è stata fornita un'API key
        if api_key:
            # Utilizza l'API key per l'autenticazione
            params = dict()
            params["text"] = kwargs["text"]
            params["version"] = kwargs["version"]
            params["features"] = kwargs["features"]
            params["return_analyzed_text"] = kwargs["return_analyzed_text"]
            params["language"] = kwargs["language"]
            response = requests.get(url,
                                    params=params,
                                    headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', api_key))
        else:
            # Nessuna autenticazione se l'API key non è stata fornita
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    try:
        response = requests.post(url, json=json_payload, params=kwargs)
        response.raise_for_status()  # Solleva un'eccezione per codici di stato HTTP non 2xx
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Error:", err)

    try:
        response_json = response.json()
        return response_json
    except json.JSONDecodeError:
        print("Invalid JSON response:", response.text)
        return None





# get_dealerships in views.py--------------------------------------------------------------------------
# get_dealers_from_cf in realtà frutta la GET dal file /functions/get-dealership.js.
# Il percoso della GET è definito in views.py con la funzione get_dealerships
# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)
    return results 





# get_dealer_details in views.py-----------------------------------------------------------------------------------------

# get_dealer_reviews_from_cf in realtà frutta la GET dal file /functions/reviews.py.
# Il percoso della GET è definito in views.py con la funzione get_dealer_details
# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_by_id_from_cf(url, dealerId):
    #(print(url))
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, id=dealerId)
    #print(json_result)
    if json_result:
        # Get the row list in JSON as reviews
        reviews = json_result
        # For each review object
        for review in reviews:
            # Get its content in `doc` object
            review_doc = review
            # Create a DealerView object with values in `doc` object
            #print(review_doc)
            review_obj = DealerReview(
                dealership=review_doc["dealership"],
                id=review_doc["id"],
                name=review_doc["name"],
                purchase=review_doc["purchase"],
                review=review_doc["review"],
                purchase_date=review_doc["purchase_date"],
                car_make=review_doc["car_make"],
                car_model=review_doc["car_model"],
                car_year=review_doc["car_year"],
                sentiment=analyze_review_sentiments(review_doc["review"])
            )
            results.append(review_obj)
    return results



# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(dealerreview):
    # URL per l'analisi delle recensioni con Watson NLU
    url = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/ac6de5ec-329d-48a2-8e75-f27649610dce/v1/analyze"

    # Parametri necessari per l'analisi delle recensioni
    params = {
        "text": dealerreview,
        "version": "2022-04-07",
        "features": "sentiment",
        "return_analyzed_text": True,
        "language": "it"
    }

    # Chiama la funzione get_request per ottenere l'analisi delle recensioni
    api_key = "S-_aUn1lR_nFT8Tnajvttdvkbk33ksaQOsZoKGDwsEMd"
    response = get_request(url, api_key=api_key, **params)
    sentiment_label=response["sentiment"]["document"]["label"]
    
    return sentiment_label

