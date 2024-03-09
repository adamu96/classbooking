import valley
import pandas as pd
from datetime import datetime, timedelta

# TODO: wait until 6AM


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

    valley.addToBasket(activity_id, activity_name)
    valley.checkout()
    
    # TODO: check for errors

    # TODO: add to google calendar?