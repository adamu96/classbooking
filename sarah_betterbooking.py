import better
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='sarah_better.log', encoding='utf-8', level=logging.DEBUG)

logger.info(f'Running Booking: {datetime.today()}')
# credentials
auth = 'Bearer v4.local.SAyn8MyVR9Ywe8Pvw574NM6rFBqSRYTXKXOTNdyIUQx5CwSgtvfHuvwACDo_NR1-3ngOcvYXtbUYGl4zn8Pc6PuJ79JeXx2NYOwjX-jdnGLHFj9T3cbZ_9P5RMwNVeFR2nrkeBdEJo-P5PeleWYwfiO6mKaW1k0WT-gE-XtGKYzIgOrP0PVCtTd5V8VMrZDDh3qHAVgqToCvCARlPw'
member_id = 2988951
activity = 'fitness-classes-c'

preferences = pd.DataFrame({'gym': ['better-gym-connswater',
                                    'better-gym-connswater',
                                    'templemore-baths'],
                            'name': ['Legs, Bums and Tums',
                                     'Legs, Bums and Tums',
                                     'Yoga'],
                            'day': ['Monday',
                                    'Wednesday',
                                    'Saturday'],
                            'hour': [18, 
                                     19, 
                                     11]
                            })

next_week = datetime.today() + timedelta(days=7)
date = next_week.strftime('%Y-%m-%d')
day_name = next_week.strftime('%A')

if preferences[preferences['day'] == day_name].empty:
    logger.error('Wrong day')
    exit()

preference_today = preferences[preferences['day'] == day_name]

slots = better.connswaterClasses(auth, date, preference_today.gym.values[0], activity)


class_slots = slots[slots['name'] == preference_today.name.values[0]]
class_slots = class_slots[class_slots['hour'] == preference_today.hour.values[0]]

booking_successful = 0
tries = 0
while not booking_successful:
    if class_slots['spaces'].values[0] > 0:
        if '401' in better.connswaterAddtoBasket(auth, member_id, str(class_slots['id'].values[0]), date):
            logger.error('auth issues')
            break
        if '422' in better.checkout(auth):
            logger.error('Basket empty')
        else:
            booking_successful = 1
            break
    else: logger.error('No spaces avaialable')
    tries+=1
    if tries >= 20: break
    logger.error('Attempt:', tries)

if booking_successful == 0: logger.error('Unsuccessfull')
else: logger.info(f'Booking Confirmed: {preference_today.name.values[0]} {date} {preference_today.hour.values[0]}')
