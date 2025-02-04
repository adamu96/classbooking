import requests
import pandas as pd
import ast
from datetime import datetime, timedelta
import time
import requests
import json

def getToken():
    headers = {
        'accept': 'application/json',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'content-type': 'application/json',
        'origin': 'https://bookings.better.org.uk',
        'priority': 'u=1, i',
        'referer': 'https://bookings.better.org.uk/',
        'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
    }

    json_data = {
        'username': 'BET4470679',
        'password': 'Jordanstown-125',
    }

    response = requests.post('https://better-admin.org.uk/api/auth/customer/login', headers=headers, json=json_data)

    token = json.loads(response.text)['token']

    return token



def connswaterClasses(auth, date, gym, activity):
    headers = {
        'accept': 'application/json',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'authorization': auth,
        'origin': 'https://bookings.better.org.uk',
        'priority': 'u=1, i',
        'referer': f'https://bookings.better.org.uk/location/{gym}/{activity}/{date}/by-time',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    }

    params = {
        'date': {date},
    }

    response = requests.get(
        f'https://better-admin.org.uk/api/activities/venue/{gym}/activity/{activity}/timetable',
        params=params,
        headers=headers,
    )

    sessions_text = cleanseResponse(response.text)
    sessions_df = pd.DataFrame(ast.literal_eval(sessions_text[:-1]))
    if date == datetime.today().strftime('%Y-%m-%d'):
        sessions_df = sessions_df.transpose()
    if sessions_df.empty:
        return 
    
    sessions_df = pd.concat([sessions_df.drop(['starts_at'], axis=1), sessions_df['starts_at'].apply(pd.Series)], axis=1)
    sessions_df = pd.concat([sessions_df.drop(['date'], axis=1), sessions_df['date'].apply(pd.Series)], axis=1)
    sessions_df = sessions_df[['id', 'raw', 'name', 'format_24_hour', 'spaces']]
    sessions_df['format_24_hour'] = pd.to_datetime(sessions_df.format_24_hour, format='%H:%M')
    sessions_df['hour'] = pd.to_numeric(sessions_df.format_24_hour.dt.hour)
    sessions_df['datetime'] = sessions_df['raw'] + sessions_df['hour'].astype(str)
    sessions_df['weekday'] = pd.to_datetime(sessions_df['raw'], format="%Y-%m-%d").dt.day_name()
    
    return sessions_df

def connswaterAddtoBasket(auth, member_id, session_id, date):
    headers = {
        'accept': 'application/json',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'authorization': auth,
        'content-type': 'application/json',
        'origin': 'https://bookings.better.org.uk',
        'priority': 'u=1, i',
        'referer': f'https://bookings.better.org.uk/location/better-gym-connswater/fitness-classes-c/{date}/by-time/class/{session_id}',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    }

    json_data = {
        'items': [
            {
                'id': session_id,
                'type': 'activity',
                'pricing_option_id': 7,
                'apply_benefit': True,
                'activity_restriction_ids': [],
            },
        ],
        'membership_user_id': member_id,
        'selected_user_id': None,
    }

    response = requests.post('https://better-admin.org.uk/api/activities/cart/add', headers=headers, json=json_data)

    return response.text


def cleanseResponse(response):
    """
    Cleans the text response for processing
    """
    return response.replace('{"data":', "").replace('false', "False").replace('null', '"null"').replace('true', "True")

def getAvailableSlots(auth, date, gym, activity):
    """
    Gets available slots for a given day
    """
    headers = {
    'accept': 'application/json',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'authorization': auth,
    'origin': 'https://bookings.better.org.uk',
    'priority': 'u=1, i',
    'referer': f'https://bookings.better.org.uk/location/{gym}/{activity}/{date}/by-time',
    'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
    }

    params = {
        'date': date,
    }

    response = requests.get(
        f'https://better-admin.org.uk/api/activities/venue/{gym}/activity/{activity}/times',
        params=params,
        headers=headers,
    )

    sessions_text = cleanseResponse(response.text)
    print(sessions_text)
    sessions_df = pd.DataFrame(ast.literal_eval(sessions_text[:-1]))
    if date == datetime.today().strftime('%Y-%m-%d'):
        sessions_df = sessions_df.transpose()
    if sessions_df.empty:
        return 
    sessions_df = pd.concat([sessions_df.drop(['starts_at'], axis=1), sessions_df['starts_at'].apply(pd.Series)], axis=1)
    sessions_df = sessions_df[['date', 'format_24_hour', 'spaces']]
    sessions_df['format_24_hour'] = pd.to_datetime(sessions_df.format_24_hour, format='%H:%M')
    sessions_df['hour'] = pd.to_numeric(sessions_df.format_24_hour.dt.hour)
    sessions_df['datetime'] = sessions_df['date'] + sessions_df['hour'].astype(str)
    sessions_df['weekday'] = pd.to_datetime(sessions_df['date'], format="%Y-%m-%d").dt.day_name()
    
    return sessions_df

def getAvailableDates(auth):
    """
    Gets all available slots for the following week
    """
    date = datetime.today() if time.strptime(datetime.now().strftime('%H:%M'), '%H:%M') < time.strptime('22:00', '%H:%M') else datetime.today() + timedelta(days=1)
    df = getAvailableSlots(auth, date.strftime('%Y-%m-%d'))
    for _ in range(1, 7):
        date = date + timedelta(1)
        df = pd.concat([df, getAvailableSlots(auth, date.strftime('%Y-%m-%d'))])
    return df

def checkCourts(auth, date, time: int):
    """
    Given a specific datetime, check available courts and get session id
    """
    if time == 9:
        start_time = '09:00'
    else:
        start_time = str(time) + ':00'

    end_time = str(time+1) + ':00' 

    headers = {
        'authority': 'better-admin.org.uk',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'authorization': auth,
        'origin': 'https://bookings.better.org.uk',
        'referer': f'https://bookings.better.org.uk/location/indoor-tennis-centre-and-ozone-complex/tennis-court-indoor/{date}/by-time/slot/{start_time}-{end_time}',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    response = requests.get(
        f'https://better-admin.org.uk/api/activities/venue/indoor-tennis-centre-and-ozone-complex/activity/tennis-court-indoor/slots?date={date}&start_time={start_time}&end_time={end_time}',
        headers=headers,
    )

    available_courts_text = response.text
    available_courts_text = cleanseResponse(available_courts_text)
    available_courts_df = pd.DataFrame(ast.literal_eval(available_courts_text[:-1]))
    available_courts_df = available_courts_df.rename(columns={'id': 'session_id'})
    available_courts_df = pd.concat([available_courts_df.drop(['location', 'name'], axis=1), available_courts_df['location'].apply(pd.Series)], axis=1)
    available_courts_df['court'] = pd.to_numeric(available_courts_df['name'].str.slice(-1))
    
    return available_courts_df

def addToBasket(auth, member_id, session_id: int, date, time: int):
    """
    add a specified session to your basket
    """
    start_time = str(time) + ':00'
    end_time = str(time+1) + ':00'

    headers = {
        'authority': 'better-admin.org.uk',
        'accept': 'application/json',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'authorization': auth,
        'content-type': 'application/json',
        'origin': 'https://bookings.better.org.uk',
        'referer': f'https://bookings.better.org.uk/location/indoor-tennis-centre-and-ozone-complex/tennis-court-indoor/{date}/by-time/slot/{start_time}-{end_time}',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    json_data = {
        'items': [
            {
                'id': session_id,
                'type': 'activity',
                'pricing_option_id': 3013,
                'apply_benefit': True,
                'activity_restriction_ids': [],
            },
        ],
        'membership_user_id': member_id,
        'selected_user_id': None,
    }

    response = requests.post('https://better-admin.org.uk/api/activities/cart/add', headers=headers, json=json_data)

    return response.text

def checkout(auth):
    """
    complete checkout on whatever is in your basket
    """
    headers = {
    'authority': 'better-admin.org.uk',
    'accept': 'application/json',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'authorization': auth,
    'content-type': 'application/json',
    'origin': 'https://bookings.better.org.uk',
    'referer': 'https://bookings.better.org.uk/basket/checkout',
    'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
}

    json_data = {
        'completed_waivers': [],
        'payments': [],
        'selected_user_id': None,
        'source': 'activity-booking',
        'terms': [
            1,
        ],
    }

    response = requests.post('https://better-admin.org.uk/api/checkout/complete', headers=headers, json=json_data)
    return response.text

def viewBookings(auth):
    headers = {
    'authority': 'better-admin.org.uk',
    'accept': 'application/json',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'authorization': auth,
    'origin': 'https://myaccount.better.org.uk',
    'referer': 'https://myaccount.better.org.uk/bookings/upcoming',
    'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
}

    params = {
        'filter': 'future',
    }

    response = requests.get('https://better-admin.org.uk/api/my-account/bookings', params=params, headers=headers)
    print(response.text)

    bookings = cleanseResponse(response.text)
    bookings = pd.DataFrame(ast.literal_eval(bookings[:-1]))
    bookings['court'] = bookings['item'][0]['location']['name']
    print(bookings['date'])
    bookings['date'] = pd.to_datetime(bookings.date)
    print(bookings['date'])
    bookings['hour'] = pd.to_numeric(bookings.time.str.slice(0,2))
    bookings['datetime'] = bookings['date'].astype(str) + bookings['hour'].astype(str)
    bookings = bookings[['date', 'hour', 'datetime', 'court']]
    
    return bookings


if __name__ == '__main__':
    # print(connswaterClasses( 'test', #'Bearer v4.local.SAyn8MyVR9Ywe8Pvw574NM6rFBqSRYTXKXOTNdyIUQx5CwSgtvfHuvwACDo_NR1-3ngOcvYXtbUYGl4zn8Pc6PuJ79JeXx2NYOwjX-jdnGLHFj9T3cbZ_9P5RMwNVeFR2nrkeBdEJo-P5PeleWYwfiO6mKaW1k0WT-gE-XtGKYzIgOrP0PVCtTd5V8VMrZDDh3qHAVgqToCvCARlPw',
    #                         '2024-11-18',
    #                         'better-gym-connswater',
    #                         'fitness-classes-c'))
    print(connswaterAddtoBasket('Bearer v4.local.SAyn8MyVR9Ywe8Pvw574NM6rFBqSRYTXKXOTNdyIUQx5CwSgtvfHuvwACDo_NR1-3ngOcvYXtbUYGl4zn8Pc6PuJ79JeXx2NYOwjX-jdnGLHFj9T3cbZ_9P5RMwNVeFR2nrkeBdEJo-P5PeleWYwfiO6mKaW1k0WT-gE-XtGKYzIgOrP0PVCtTd5V8VMrZDDh3qHAVgqToCvCARlPw',
                                2988951,
                                61313807,
                                '2024-11-11'))
