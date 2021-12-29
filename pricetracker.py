import bs4
import requests
import csv
import os.path
import smtplib
import json
from time import time, ctime, strptime, mktime


def get_soup_object(product_urls):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": 'https://google.com',
        "DNT": "1",
        "Connection": "close",
        "Upgrade-Insecure-Requests": "1"
    }
    r = requests.get(product_urls, headers=headers)
    r.raise_for_status()

    soup = bs4.BeautifulSoup(r.text, 'html.parser')
    return soup


def get_amazon_info(soup):
    name = soup.find_all('span', {'id': 'productTitle'})
    shortened_name = name[0].text.strip()[:25] + '...'
    price = soup.find_all('span', {'class': 'a-offscreen'})
    return shortened_name, price[0].text


def send_email(url, name, price, cutoff, alert_type, time_elapsed=0):
    EMAIL_ADDRESS = os.environ.get('EMAIL_USER')
    EMAIL_PASS = os.environ.get('EMAIL_PASS')

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:  # arguments: mail server, port
        smtp.ehlo()  # identify ourself with the mail server we're using
        smtp.starttls()  # encrypt traffic
        smtp.ehlo()  # re-identify ourself as an encrypted connection

        smtp.login(EMAIL_ADDRESS, EMAIL_PASS)  # login to mail server

        if alert_type == 'price_drop':
            subject = f'Price Drop Alert for {name}'
            body = f'{name} has dropped below ${cutoff}! Get it for ${price} at {url}.'
            msg = f'Subject: {subject}\n\n{body}'

        elif alert_type == 'reminder':
            subject = f'{name} is still on sale!'
            body = f'{name} dropped below ${cutoff} about {time_elapsed} hours ago! Get it at {url} before the deal expires!'
            msg = f'Subject: {subject}\n\n{body}'

        else:  # elif alert_type == 'price_increase':
            subject = f'{name} is no longer on sale'
            body = f'You missed your chance to buy {name} while it was under ${cutoff}.\nBut don\'t worry, we\'ll send you another email when it goes on sale again!'
            msg = f'Subject: {subject}\n\n{body}'

        try:
            smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg)  # arguments: sender, receiver, message
        except UnboundLocalError as e:
            print(e)


# Update the status of a particular type of email notification
def update_status(url, alert_type, state):
    with open('emails.json', 'r+') as f:
        json_object = json.load(f)
        json_object[url][alert_type] = state

        # TODO: Take the time to understand f.seek() and f.truncate()
        f.seek(0)
        json.dump(json_object, f, indent=4)
        f.truncate()


# Get the time since epoch in seconds of the last price alert/reminder
def get_time_elapsed(url, current_time):
    with open('price_history') as f:
        rows = csv.DictReader(f)

        product_timestamps = []
        for row in rows:
            if row['Product URL'] == url:
                product_timestamps.append(row['Timestamp'])

        # Convert the last timestamp from a string to an int (seconds)
        last_timestamp = product_timestamps[-1]
        # Sat Nov 27 15:41:17 2021
        x = strptime(last_timestamp, '%a %b %d %H:%M:%S %Y')
        previous_time = mktime(x)
        time_difference = (current_time - previous_time) / 3600

    return time_difference


# TODO: Create interactive plot from csv data. Maybe consider writing this in a new file?
def create_plot():
    pass



def main():
    current_time = time()

    product_info = {
        'https://www.amazon.com/Acer-Octa-Core-Processor-Fingerprint-SF314-42-R9YN/dp/B08C5DJCXX/ref=sr_1_2?crid=7VQ69OOF661&keywords=sf314-511-51a3&qid=1637106608&qsid=131-0211403-8502744&s=electronics&sprefix=-511-51A3%2Celectronics%2C230&sr=1-2&sres=B08JQJ5RKK%2CB08C5DJCXX%2CB078211KBB%2CB086KJBKDW%2CB086KKKT15%2CB0866PQXKH%2CB07RF1XD36%2CB07DFKTKGG%2CB07RHQGS8V%2CB094MJ86LG%2CB08X6YQXRL%2CB01MTOLJ2V%2CB09DT646FQ%2CB09GLYD7PH%2CB07BJT451N%2CB07GNFSWCS%2CB08ZNWMDTK%2CB06XWNF87W%2CB0793T8L4Y%2CB08SW2RC6V&th=1'
        : {
            'price_cutoff': 500
        },
        'https://www.amazon.com/HP-Portable-Micro-Edge-Anti-Glare-14-fq1021nr/dp/B091D9652Z?linkCode=ll1&tag=briisdeals07-20&linkId=b8c3237ab9fd07a1ca4a44c6ba6b6b61&language=en_US&ref_=as_li_ss_tl&fbclid=IwAR2RpM7SvB1H2TLHtg7YYAYSDc18kAllLn5mhISmRwAOiDy5QQRcrfmxgOw&th=1'
        : {
            'price_cutoff': 450
        },
        'https://www.amazon.com/Lenovo-IdeaPad-Processor-Graphics-81W0003QUS/dp/B0862269YP'
        : {
            'price_cutoff': 525
        },
        'https://www.amazon.com/PETKIT-EVERSWEET-Automatic-Water-Shortage-Filter-Change/dp/B07H7J4PBQ/ref=sr_1_5?keywords=cat+water+fountain+no+led&qid=1637481369&qsid=131-0211403-8502744&sr=8-5&sres=B07SMPC3MD%2CB07F5KRPF2%2CB07SBXDMZQ%2CB07H7J4PBQ%2CB089F9YSGL%2CB07ZHZTWSH%2CB08ZN76HLW%2CB08NKG7QJ4%2CB09CY4DJ12%2CB08FR8QJV8%2CB07525CQ4C%2CB081Z6DB8B%2CB092V3C669%2CB0932WNZL2%2CB09BN94XPH%2CB07DLXF7XL%2CB07MKSC82B%2CB08ZCY1FJT%2CB09956HPSW%2CB087JR9YMX#'
        : {
            'price_cutoff': 50
        }
    }

    for url in product_info:
        # Populate product_info with product's name and price
        soup = get_soup_object(url)
        name, price = get_amazon_info(soup)
        product_info[url]['name'] = name
        product_info[url]['price'] = price
        cutoff = product_info[url]['price_cutoff']

        # Remove dollar sign from the price and convert it from a string to a float 
        price = float(price[1:])

        # Read json data about which type of email notifications have already been sent
        f = open('emails.json')
        json_object = json.load(f)
        f.close()

        # Send the correct email notification based on what type of notification has already been sent
        if price <= cutoff:
            try:
                time_elapsed_hours = round(get_time_elapsed(url, current_time))
            except:
                time_elapsed_hours = 0

            # If a price drop alert hasn't been sent already, send it
            if not json_object[url]['price_drop']:
                send_email(url, name, price, cutoff, 'price_drop')
                update_status(url, 'price_drop', True)

            # If price drop alert has been sent and a reminder hasn't already been sent after 6 hours, send it
            elif not json_object[url]['reminder'] and time_elapsed_hours >= 6:
                send_email(url, name, price, cutoff, 'reminder', time_elapsed=time_elapsed_hours)

        # Reset states of price drop alerts and reminders if the price increases
        elif price > cutoff and json_object[url]['price_drop']:
            send_email(url, name, price, cutoff, 'price_increase')
            update_status(url, 'price_drop', False)
            update_status(url, 'reminder', False)

    file_name = 'price_history.csv'

    # Store data into a csv file
    with open(file_name, 'a', newline='') as csv_file:
        file_is_empty = os.stat(file_name).st_size == 0

        fieldnames = ['Product Name', 'Timestamp', 'Product Price', 'Product URL']
        rows = csv.DictWriter(csv_file, fieldnames=fieldnames)

        if file_is_empty:
            rows.writeheader()

        for url in product_info:
            rows.writerow({'Product Name': product_info[url]['name'], 'Timestamp': ctime(), 'Product Price': product_info[url]['price'],
                           'Product URL': url})


main()

# Ideas for future implementations:
# Somehow make the program automatically run once or twice a day using windows task scheduler
# Store the lowest price for that day and other product info into a csv file
# Plot the price over time with some module like pandas or matplotlib and update the graph once eveyrday
# Automatically send an email when the price dips below a certain point
# Maybe use sys timeout in your for loop to lower the frequency of requests?

# Make this code web-based
# It'd be cool to make graph interactive. E.g., mouse over a certain point on the graph and have a popup of the price
