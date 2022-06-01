import pytest
from datetime import datetime
from application import db
from application.bbwrapper import ProductInfo
from application.helpers import update_product_info
from application.models import User, Product, UserPreferences, UserProduct

"""
1. Update existing product's price to FAKE_HIGH_PRICE
2. Run update function
3. Check that actual price FAKE_HIGH_PRICE
"""

FAKE_HIGH_PRICE = 100000

@pytest.fixture
def update_price():
    def _update_price(product_db_object):
        product_db_object.price = FAKE_HIGH_PRICE
        db.session.commit()
    return _update_price

def test_update(update_price):
    # breakpoint()
    test_user = UserPreferences.query.filter_by(all_notifications_disabled=False).first().user
    test_asso = UserProduct.query.filter_by(user_id=test_user.id).first()
    test_product = test_asso.product
    test_asso.next_notification = "primary"
    update_price(test_product)
    update_product_info()
    assert (float(test_product.price) < FAKE_HIGH_PRICE)
    assert (test_asso.next_notification == "reminder")

    # test if changed back to primary upon price increase 
    test_asso.last_updated = datetime.fromtimestamp(76204800) # arbitrary time near epoch
    db.session.commit()
    update_price(test_product)
    update_product_info()
    assert (test_asso.next_notification == "primary")

# test if product is NOT being updated per user's account settings
@pytest.mark.skip(reason="for later")
def test_account_preferences():
    pass
