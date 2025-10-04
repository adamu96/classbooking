import archive.valley as valley
import pandas as pd
from datetime import datetime, timedelta
from time import sleep
import json
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(filename='valley.log', encoding='utf-8', level=logging.DEBUG)

logger.info(f'Running Booking: {datetime.today()}')
current_weekday = datetime.today().isoweekday()
preferences = pd.DataFrame({'day': [2, 4, 5], 'activity': ['PILATES', 'PILATES', 'YOGA'], 'time': [10, 10, 10]})

if not preferences[preferences['day'] == current_weekday].empty:
    activity_name = preferences[preferences.day == current_weekday].activity.values[0]
    activity_time = preferences[preferences.day == current_weekday].time.values[0]
if not preferences[preferences['day'] == current_weekday].empty:
    activity_name = preferences[preferences.day == current_weekday].activity.values[0]
    activity_time = preferences[preferences.day == current_weekday].time.values[0]

    booking_date = datetime.today() + timedelta(days=7)
    booking_date = booking_date.date()
    booking_date = datetime.today() + timedelta(days=7)
    booking_date = booking_date.date()

    slots = valley.getAvailableSlots()
    activity_id = slots[(slots['datetime'].dt.hour == activity_time) &
                        (slots['datetime'].dt.date == booking_date) &
                        (slots['title'] == activity_name)].ActivityInstanceID.values[0]
    slots = valley.getAvailableSlots()
    activity_id = slots[(slots['datetime'].dt.hour == activity_time) &
                        (slots['datetime'].dt.date == booking_date) &
                        (slots['title'] == activity_name)].ActivityInstanceID.values[0]

    basket = json.loads(valley.addToBasket(activity_id, activity_name))
    basket = json.loads(valley.addToBasket(activity_id, activity_name))

    if basket['Success']:
        checkout = valley.checkout()
        if "paymentconfirmation" in checkout:
            logger.info(f'Booking Confirmed: {activity_name} {booking_date} {activity_time}')
    else: logger.error(f'{basket["ErrorMessage"]} ({activity_name} {booking_date} {activity_time}:00)')
