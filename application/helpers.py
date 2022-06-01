from datetime import datetime
from application.models import User, Product, UserPreferences, UserProduct
from application import db
from application.bbwrapper import ProductInfo
from time import sleep


def create_product_info(db_product):
    product_object = ProductInfo(sku=db_product.sku)
    product_object.set_primary_info()
    product_object.save_product_image()
    return product_object


def update_db(db_product, product):
    db_product.sku=product.sku
    db_product.name=product.name
    db_product.price=product.price
    db_product.is_available=product.is_available
    db_product.url=product.page_url
    db_product.image_file=product.image_filename
    db.session.commit()


def update_product_info():
    results = db.session.query(User, UserPreferences) \
        .join(UserPreferences) \
        .filter(UserPreferences.all_notifications_disabled == False) \
        .all()
    subscribed_users = [d[0] for d in results]
    primary_emails = reminder_emails = []
    now = datetime.now()

    for user in subscribed_users:
        # breakpoint()
        reminders_on = not user.user_preferences.reminders_disabled
        associations = UserProduct.query.filter_by(user=user).all()
        # UserProduct object
        assos_primary = [asso for asso in associations if asso.next_notification == "primary"]
        for asso in assos_primary:
            product_info = create_product_info(asso.product)
            if float(product_info.price) <= asso.price_cutoff:
                primary_emails.append(asso)                 # create list of assos which has info about user & on-sale product
                asso.next_notification = "reminder"
            update_db(asso.product, product_info)
            # sleep(3)  # prevent api timeouts

        if reminders_on:
            assos_reminder = [asso for asso in associations if asso.next_notification == "reminder"]
            for asso in assos_reminder:
                product_info = create_product_info(asso.product)
                hours = get_hours_elapsed(asso.last_updated, now)
                reminder_freq = user.user_preferences.reminder_freq
                if hours >= reminder_freq and float(product_info.price) <= asso.price_cutoff:
                    reminder_emails.append(asso)
                    # can set notif_type back to primary if you decide better UX = only send reminder once
                else:
                    asso.next_notification = "primary" # stop sending reminders once price goes back up
                update_db(asso.product, product_info)
                # sleep(3)

        send_emails(primary_emails, reminder_emails)
        print(primary_emails)


def send_emails(primary_emails=None, reminder_emails=None):
    pass


def get_hours_elapsed(last_updated, now):
    time_elapsed = now - last_updated
    return int(time_elapsed.total_seconds() / 3600)


def get_mins_elapsed(last_updated, now):
    time_elapsed = now - last_updated
    return int(time_elapsed.total_seconds() / 60)
