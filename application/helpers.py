from datetime import datetime
from application.models import User, Product, UserPreferences, UserProduct
from application import db
from application.bbwrapper import ProductInfo
from time import sleep


def create_product(db_product):
    product_object = ProductInfo(sku=db_product.sku)
    product_object.set_primary_info()
    product_object.save_product_image()
    return product_object


def update_product_info():
    print("hello")
    pass
    all_users = User.query.all()
    results = db.session.query(User, UserPreferences) \
        .join(UserPreferences) \
        .filter(UserPreferences.all_notifications_disabled == False) \
        .all()
    subscribed_users = [d[0] for d in results]
    primary_emails = reminder_emails = []
    now = datetime.now()

    for user in subscribed_users:
        reminders_on = user.user_preferences.reminders_disabled
        associations = UserProduct.query.filter_by(user=user).all()
        # UserProduct object
        assos_primary = [asso for asso in associations if asso.next_notification == "primary"]
        for asso in assos_primary:
            # seems a bit expensive.. not sure if I want to do this everytime
            product = create_product(asso.product)
            if float(product.price) <= asso.price_cutoff:
                # create list of assos which has info about user & on-sale product
                primary_emails.append(asso)
                asso.next_notification = "reminder"
            sleep(3)  # prevent api timeouts

        if reminders_on:
            # UserProduct object
            assos_reminder = [asso for asso in associations if asso.next_notification == "reminder"]
            for asso in assos_reminder:
                product = create_product(asso.product)
                hours = get_hours_elapsed(asso.product.last_update, now)
                reminder_freq = user.user_preferences.reminder_freq
                if hours >= reminder_freq and float(product.price) <= asso.price_cutoff:
                    reminder_emails.append(asso)
                    # can set notif_type back to primary if you decide better UX = only send reminder once
                else:
                    # stop sending reminders once price goes back up
                    asso.next_notification = "primary"
                sleep(3)

        send_emails(primary_emails, reminder_emails)


def send_emails():
    pass


def get_hours_elapsed(last_updated, now):
    time_elapsed = now - last_updated
    return int(time_elapsed.total_seconds() / 3600)


def get_mins_elapsed(last_updated, now):
    time_elapsed = now - last_updated
    return int(time_elapsed.total_seconds() / 60)
