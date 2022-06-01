from application.bbwrapper import session
import requests
import shutil
import json
import re
import os


class ProductInfo:
    def __init__(self, url=None, sku=None):
        if sku is None and url is None:
            raise ValueError(
                "Must provide either a product url or product sku")
        elif sku is None and url is not None:
            self.sku = self.get_product_sku(url)
        else:
            self.url = url
            self.sku = sku
        # self.name = None
        # self.price = None
        # self.is_available = None
        # self.image_url = None

    def get_product_sku(self, url):
        domain_regex = re.compile(r'skuId=(\d{7})', re.IGNORECASE)
        mo = domain_regex.search(url)
        if mo:
            return mo.groups()[0]
        else:
            raise ValueError(
                "Could not find the product SKU in the provided URL.")

    def set_primary_info(self):
        path = f"https://api.bestbuy.com/v1/products(sku={self.sku})?sort=salePrice.asc&show=salePrice,onlineAvailability,name,image,url&format=json"
        try:
            res = session.get(path)
            self.price, self.is_available, self.name, self.image_url, self.page_url = res.json()["products"][0].values()
        except:
            raise requests.RequestException(res.status_code)

    def save_product_image(self):
        script_dir = os.path.dirname(os.path.realpath('__file__'))
        rel_path = "application/static/product_images"
        self.image_filename = f'{self.sku}.png'
        abs_path = os.path.join(script_dir, rel_path, self.image_filename)

        headers = {'User-agent': 'Mozilla/5.0'}
        res = requests.get(self.image_url, headers=headers).content
        with open(abs_path, 'wb') as f:
            f.write(res)

    def __repr__(self):
        return self.name
