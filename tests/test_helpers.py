import pytest
from application import db
from application.bbwrapper import ProductInfo
from application.helpers import update_product_info
from application.models import User, Product, UserPreferences, UserProduct

"""
1. Create fake db product with different price and high price cutoff with a real sku
2. Run helper function
3. Query product with same sku
4. See if product price was updated in db
5. Check if email list was populated
"""

TEST_SKU = "6487447"
TEST_URL = "https://www.bestbuy.com/site/apple-iphone-13-pro-max-5g-128gb-alpine-green-t-mobile/6487447.p?skuId=6487447#anchor=productVariations"
test_product = ProductInfo(sku=TEST_SKU)
actual_price = test_product.price

pytest.fixture()
def create_product():
    product = Product(
        sku=test_product.sku,
        name=test_product.name,
        price=10000, # artificial price
        is_available=test_product.is_available,
        url=test_product.url,
        image_file=test_product.image_filename
    )
    db.commit()

def test_update(create_product):
    update_product_info()
    product = Product.query.filter_by(sku=TEST_SKU).first()
    assert(product.price == actual_price)
