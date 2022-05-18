from dotenv import load_dotenv
import os
import requests

load_dotenv()
BEST_BUY_API_KEY = os.environ["BEST_BUY_API_KEY"]

class APIKeyMissingError(Exception):
    pass

if not BEST_BUY_API_KEY:
    raise APIKeyMissingError(
        "All methods require an API Key. See "
        "https://bestbuyapis.github.io/api-documentation/#get-a-key "
        "for how to get one."
    )

session = requests.Session()
session.params['apiKey'] = BEST_BUY_API_KEY

from application.bbwrapper.ProductInfo import ProductInfo
