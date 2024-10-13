import better
import pandas as pd
from datetime import datetime, timedelta

# credentials
auth = 'Bearer v4.local.lGjbgJkKYg5SUUDc19vuFS3HxiElCsHhyR8i2lxQdeuxmtXJRdyyEY1CVCq76PvVrMIiAiJRWDwX1QObu7TeXU9VF8g4hNDHZ_LniNePjiRnKAkUb74pQfo4ZxWs1YPYhF8uAq5dnipONDkyk0QWua1Cq-0buufkHY3FNwxqq0nBlz_CJRSx2YmB_azs-zrgR1ptMwTyrNqNxOed4w'
member_id = 2848350
gym = 'better-gym-connswater'
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
    print('wrong day')
    exit()

preference_today = preferences[preferences['day'] == day_name]

slots = better.connswaterClasses(auth, date, preference_today.gym.values[0], activity)


class_slots = slots[slots['name'] == preference_today.name.values[0]]
class_slots = class_slots[class_slots['hour'] == preference_today.hour.values[0]]

print(class_slots)

booking_successful = 0
tries = 0
while not booking_successful:
    if class_slots['spaces'].values[0] > 0:
        print(better.connswaterAddtoBasket(auth, member_id, str(class_slots['id'].values[0]), date))
        if '422' in better.checkout(auth):
         print('basket empty')
        else:
            booking_successful = 1
            break
    else: print('no spaces avaialable')
    tries+=1
    if tries >= 20: break
    print('attempt:', tries)

if booking_successful == 0: print('unsuccessful')
else: print('booking successful')
