import pytest
import os
from application.bbwrapper.ProductInfo import ProductInfo

@pytest.fixture
def product_attributes():
    return ["url", "sku", "name", "price", "is_available", "image_url", "page_url"]

TEST_SKU = "6487447"
TEST_URL = "https://www.bestbuy.com/site/apple-iphone-13-pro-max-5g-128gb-alpine-green-t-mobile/6487447.p?skuId=6487447#anchor=productVariations"
test_product = ProductInfo(sku=TEST_SKU)


def test_constructor():
    assert (test_product.sku)

    # test if sku is populated if only url is provided 
    test_product_2 = ProductInfo(url=TEST_URL)
    assert (test_product_2.sku)


def test_primary_info(product_attributes):
    # test setters
    test_product.set_primary_info()
    assert set(test_product.__dict__.keys()).issubset(product_attributes)


def test_get_product_sku():
    valid_url = TEST_URL
    invalid_url = "https://www.bestbuy.com"

    assert (test_product.get_product_sku(valid_url) == TEST_SKU)

    with pytest.raises(ValueError) as context:
        test_product.get_product_sku(invalid_url)
    assert str(context.value) == "Could not find the product SKU in the provided URL." 


def test_save_product_img():
    test_product.save_product_image()
    script_dir = os.path.dirname(os.path.realpath('__file__'))
    parent_folder = os.path.join(script_dir, "application/static/product_images")

    assert (test_product.image_filename)
    
    # test if product image saved to correct folder
    assert (os.path.isfile(f"{parent_folder}/{test_product.image_filename}")) 


@pytest.mark.skip(reason="debating if this should be a method")
def test_get_name_and_img():
    response = test_product.get_product_name_and_img()
    assert response["products"][0]["image"] and response["products"][0]["name"]