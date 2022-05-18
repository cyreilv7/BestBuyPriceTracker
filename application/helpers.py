from datetime import datetime

def update_product_info():
    pass


def check_against_cutoff():
    pass


def get_hours_elapsed(last_updated, now):
    time_elapsed = now - last_updated 
    return int(time_elapsed.total_seconds() / 3600)


def get_mins_elapsed(last_updated, now):
    time_elapsed = now - last_updated
    return int(time_elapsed.total_seconds() / 60) 
