import better
import pandas as pd
from datetime import datetime, timedelta
from googleapi import addCalendarEvent, sendGmail


# credentials
auth = 'Bearer '+ better.getToken()
member_id = 2945507
gym = 'indoor-tennis-centre-and-ozone-complex'
activity = 'tennis-court-indoor'

next_week = datetime.today() + timedelta(days=7)
date = next_week.strftime('%Y-%m-%d')
day_name = next_week.strftime('%A')

print(day_name, date)


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
    priority_slots = pd.merge(better.getAvailableSlots(auth, date),
                          datetime_preferences, on='hour', how='inner').sort_values(by='priority')
except:
    print('date outside of visible dates')
    exit()

booking_successful = 0
tries = 0
while not booking_successful:
    for index, slot in priority_slots.iterrows():
        if slot.spaces > 0:
            # get available courts and session ids
            courts = pd.merge(better.checkCourts(auth, date, slot.hour), court_preferences, on='court', how='inner')
            courts = courts[courts['spaces'] > 0]
            # use session id to book preferred court
            for court in courts.sort_values(by='priority').court:
                for index, session in courts.iterrows():
                    if session['court'] == court:
                        print('book:', session['session_id'], 'on', date, 'at', str(slot['hour'])+':00')
                        print(better.addToBasket(auth, member_id, session['session_id'], date, slot['hour']))
                        # check response to ensure booking was successful
                        if '422' in better.checkout(auth):
                            print('basket empty')
                        else:
                            booking_successful = 1
                            print('booking successful')
                            addCalendarEvent(title='Tennis (auto)',
                                    location='Ormeau Tennis Courts',
                                    description=f'Court: {court}',
                                    start= f'{date}T{str(slot["hour"])}'+':00:00',
                                    end=f'{date}T{str(slot["hour"]+1)}'+':00:00',
                                    attendees='margretbarclay10@gmail.com')
                            sendGmail(date=date,
                                      time=str(slot['hour'])+':00',
                                      recipients="adam.urquhart96@gmail.com, margretbarclay10@gmail.com")
                            exit()
                if booking_successful:
                    break
        if booking_successful:
            break
    tries+=1
    if tries >= 20: break
    print('attempt:', tries)

if booking_successful == 0: print('no options available')
