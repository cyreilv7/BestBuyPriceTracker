from datetime import datetime
from application.models import User, Product, UserPreferences, UserProduct
from application import db
from application.bbwrapper import ProductInfo
from time import sleep
from dotenv import load_dotenv
import smtplib
import os

def create_product_info(db_product):
    product_object = ProductInfo(sku=db_product.sku)
    product_object.set_primary_info()
    product_object.save_product_image()
    return product_object


def update_db(db_product, asso, now, product):
    db_product.sku=product.sku
    db_product.name=product.name
    db_product.price=product.price
    db_product.is_available=product.is_available
    db_product.url=product.page_url
    db_product.image_file=product.image_filename
    asso.last_updated = now
    db.session.commit()


def update_product_info():
    results = db.session.query(User, UserPreferences) \
        .join(UserPreferences) \
        .filter(UserPreferences.all_notifications_disabled == False) \
        .all()
    subscribed_users = [d[0] for d in results]
    primary_email_list = reminder_email_list = []
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
                primary_email_list.append(asso)                 # create list of assos which has info about user & on-sale product
                asso.next_notification = "reminder"
            update_db(asso.product, asso, now, product_info)
            sleep(3)  # prevent api rate limit 

        assos_reminder = [asso for asso in associations if asso.next_notification == "reminder"]
        for asso in assos_reminder:
            hours = get_hours_elapsed(asso.last_updated, now)
            product_info = create_product_info(asso.product)
            if hours >= (7*24):
                asso.next_notification = "primary"
                db.session.commit()
            elif reminders_on and hours >= reminder_freq and float(product_info.price) <= asso.price_cutoff:
                reminder_email_list.append(asso)

            update_db(asso.product, asso, now, product_info)
            sleep(3)
    
        send_emails(primary_email_list, reminder_email_list)


def send_emails(primary_email_list=None, reminder_email_list=None):
    load_dotenv()
    EMAIL_ADDRESS = os.environ['EMAIL_ADDRESS']
    EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        if primary_email_list:
            for asso in primary_email_list:
                subject = f'Price Drop Alert - {asso.product.name[:30]} is on sale'
                body = f'{asso.product.name} has dropped below ${asso.price_cutoff}!\n\nGet it for ${asso.product.price} at {asso.product.url}.'
                msg = f'Subject: {subject}\n\n{body}'
                smtp.sendmail(EMAIL_ADDRESS, asso.user.email, msg)

        if reminder_email_list:
            for asso in reminder_email_list:
                subject = f'{asso.product.name} is still on sale!'
                body = f'{asso.product.name} is still under ${asso.price_cutoff}. Get it at {asso.product.url} before the deal expires!'
                msg = f'Subject: {subject}\n\n{body}'
                smtp.sendmail(EMAIL_ADDRESS, asso.user.email, msg)


def get_hours_elapsed(last_updated, now):
    time_elapsed = now - last_updated
    return int(time_elapsed.total_seconds() / 3600)


def get_mins_elapsed(last_updated, now):
    time_elapsed = now - last_updated
    return int(time_elapsed.total_seconds() / 60)
