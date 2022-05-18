import pytest
from application.bbwrapper.ProductInfo import ProductInfo

@pytest.fixture
def product_keys():
    return ['salePrice', 'shippingCost', 'onlineAvailability', 'image']

@pytest.fixture
def product_attributes():
    return ["url", "sku", "name", "total_price", "price", "shipping", "is_available", "image_filename", "image_url"]


TEST_SKU = "6487447"
TEST_URL = "https://www.bestbuy.com/site/apple-iphone-13-pro-max-5g-128gb-alpine-green-t-mobile/6487447.p?skuId=6487447#anchor=productVariations"

test_product = ProductInfo(url=TEST_URL, sku=TEST_SKU)

def test_primary_info(product_attributes):
    # test constructor
    assert (test_product.sku)

    # test setters
    test_product.set_primary_info()
    assert set(test_product.__dict__.keys()).issubset(product_attributes)


def test_save_img():
    test_product.save_product_image()
    assert(test_product.image_filename)


@pytest.mark.skip()
def test_get_name_and_img():
    response = test_product.get_product_name_and_img()
    assert response["products"][0]["image"] and response["products"][0]["name"]
    
#py.test