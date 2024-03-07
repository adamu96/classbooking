import pandas as pd
import better
from datetime import datetime, timedelta
import os
# from google.cloud import bigquery
import ast
import valley
import json
import requests

# client = bigquery.Client.from_service_account_json('key.json')

auth = 'Bearer v4.local.EKvZbFP4m02EQHaGJzp-J3nzRPCx_rPl_zrBTfbDH-xn5BC1oDZb1yvYup9sJAO94OxRrmYJcSYuP44Qy3aFl3LnVmPCYkiWOvhcvc2sKxtf3L-Jm5qFBlu7rvng6s2JlXB5bwDR1Edni0H92Kq-9eF_qI6MoVC3lW8RbIN1sxuBEwO409_OWylGyf-WW6Clghp-3czmAq7SlZzfUA'
member_id = 2945507

# TODO: factor in request verification token for user
# df = valley.getAvailableSlots()

# print(df.columns)

# print(df.iloc[0])

# print(df[['ActivityInstanceID', 'title', 'start', 'AvailableSlots']])

# print(valley.addToBasket(1356201, 'YOGA'))


    # 'ActivityInstanceId': '1342379',
    # 'ActivityName': 'YOGA',

slots = valley.getAvailableSlots()
start = slots[slots['ActivityInstanceID'] == 1342379].start.values[0]
bookings = valley.viewBookings()
print(start)
print(bookings)
booking_to_cancel = bookings[bookings.StartDate == start].ReservationGUID.values[0]

print(valley.cancelBooking(booking_to_cancel))

