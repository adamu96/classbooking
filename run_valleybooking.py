import valley
import pandas as pd
from datetime import datetime, timedelta
from time import sleep
import json

# TODO: wait until 6 am to book
# note, extra while loop to stop programme from running if starting before midnight 
# while datetime.today().time() > datetime.strptime('06', "%H").time():
#     sleep(1)
while datetime.today().time() < datetime.strptime('06', "%H").time():
    sleep(1)

current_weekday = datetime.today().isoweekday()
preferences = pd.DataFrame({'day': [2, 4, 5], 'activity': ['PILATES', 'PILATES', 'YOGA'], 'time': [10, 10, 10]})

if not preferences[preferences['day'] == current_weekday].empty:
    activity_name = preferences[preferences.day == current_weekday].activity.values[0]
    activity_time = preferences[preferences.day == current_weekday].time.values[0]

    booking_date = datetime.today() + timedelta(days=7)
    booking_date = booking_date.date()

    slots = valley.getAvailableSlots()
    activity_id = slots[(slots['datetime'].dt.hour == activity_time) &
                        (slots['datetime'].dt.date == booking_date) &
                        (slots['title'] == activity_name)].ActivityInstanceID.values[0]

    basket = json.loads(valley.addToBasket(activity_id, activity_name))

    if basket['Success']:
        checkout = valley.checkout()
        if "paymentconfirmation" in checkout:
            print('Booking Confirmed:', activity_name, booking_date, activity_time)
    else: print('Error:', basket['ErrorMessage'], '(', activity_name, booking_date, activity_time, ')')
    
