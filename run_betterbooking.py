import better
import pandas as pd
from datetime import datetime, timedelta
from time import sleep
# credentials
auth = 'Bearer v4.local.EKvZbFP4m02EQHaGJzp-J3nzRPCx_rPl_zrBTfbDH-xn5BC1oDZb1yvYup9sJAO94OxRrmYJcSYuP44Qy3aFl3LnVmPCYkiWOvhcvc2sKxtf3L-Jm5qFBlu7rvng6s2JlXB5bwDR1Edni0H92Kq-9eF_qI6MoVC3lW8RbIN1sxuBEwO409_OWylGyf-WW6Clghp-3czmAq7SlZzfUA'
member_id = 2945507
gym = 'indoor-tennis-centre-and-ozone-complex'
activity = 'tennis-court-indoor'

next_week = datetime.today() + timedelta(days=7)
date = next_week.strftime('%Y-%m-%d')

# TODO: wait until 10 pm to book
while datetime.today().time() < datetime.strptime('22', "%H").time():
    sleep(1)
    
# TODO: get preferences for datetime/court
# TODO: the code should only book a time if the day is included in preferences
datetime_preferences = pd.DataFrame({'day': [1, 1, 1, 1, 1], 'hour': [19, 20, 18, 21, 17], 'priority': [1, 2, 3, 4, 5]})
# datetime_preferences = pd.DataFrame({'day': [1, 1, 1, 1, 1], 'hour': [11, 10, 12, 13, 9], 'priority': [1, 2, 3, 4, 5]})
court_preferences = pd.DataFrame({'court': [1, 2, 3, 4], 'priority': [4, 1, 2, 3]})

# check available spaces and order by priority
priority_slots = pd.merge(better.getAvailableSlots(auth, date, gym, activity), datetime_preferences, on='hour', how='inner').sort_values(by='priority')

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
                            break
                if booking_successful:
                    break
        if booking_successful:
            break
    tries+=1
    if tries >= 20: break
    print('attempt:', tries)


if booking_successful == 0: print('no options available')
else: print('booking successful')