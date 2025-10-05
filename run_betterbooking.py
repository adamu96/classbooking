from packages.better import beterClient
import pandas as pd
from datetime import datetime, timedelta
# from packages.googleapi import addCalendarEvent
# from packages.gmail import send_gmail
import logging
from logging_config import setup_logging
import os
from dotenv import load_dotenv
from packages.notifications import send_pushover_notification

load_dotenv()
setup_logging()

logger = logging.getLogger(__name__)
logger.info(f'Running Booking: {datetime.today()}')

better = beterClient()
gym = 'indoor-tennis-centre-and-ozone-complex'
activity = 'tennis-court-indoor'

next_week = datetime.today() + timedelta(days=7)
date = next_week.strftime('%Y-%m-%d')
day_name = next_week.strftime('%A')

# TODO: get preferences for datetime/court
# TODO: the code should only book a time if the day is included in preferences
if day_name == 'Saturday' or day_name == 'Sunday': datetime_preferences = pd.DataFrame({'hour': [11, 10, 12, 13, 9],
                                                                                        'priority': [1, 2, 3, 4, 5]})
else: datetime_preferences = pd.DataFrame({'hour': [19, 20, 18, 21, 17],
                                           'priority': [1, 2, 3, 4, 5]})

court_preferences = pd.DataFrame({'court': [1, 2, 3, 4], 
                                  'priority': [4, 1, 2, 3]})

# check available spaces and order by priority
try:
    priority_slots = pd.merge(better.getAvailableSlots(date, gym, activity),
                          datetime_preferences, on='hour', how='inner').sort_values(by='priority')
except Exception as e:
    logger.error('Error:', e)
    send_pushover_notification(e, 'Tennis Booking Failed')
    exit()

booking_successful = 0
tries = 0
while not booking_successful:
    for index, slot in priority_slots.iterrows():
        if slot.spaces > 0:
            # get available courts and session ids
            courts = pd.merge(better.checkCourts(date, slot.hour), court_preferences, on='court', how='inner')
            courts = courts[courts['spaces'] > 0]
            # use session id to book preferred court
            for court in courts.sort_values(by='priority').court:
                for index, session in courts.iterrows():
                    if session['court'] == court:
                        logger.info(f"book: {session['session_id']} on {date} at {str(slot['hour'])}:00")
                        logger.info(better.addToBasket(session['session_id'], date, slot['hour']))
                        # check response to ensure booking was successful
                        checkout = better.checkout()
                        if '422' in checkout:
                            print('basket empty')
                        else:
                            print(checkout)
                            booking_successful = 1
                            logger.info('booking successful')
                            send_pushover_notification(f"Tennis booked: {date} {str(slot['hour'])}:00", 
                                                       'Tennis booking successful')
                            # send_gmail(subject=f"Tennis booked: {date} {str(slot['hour'])}:00",
                                        #    message="Get yourselves out there and have fun.")
                            exit()
                if booking_successful:
                    break
        if booking_successful:
            break
    tries+=1
    if tries >= 20: break
    logger.error('Attempt:', tries)

if booking_successful == 0: 
    logger.error('no options available')
    send_pushover_notification('No options available', 'Tennis booking failed')
