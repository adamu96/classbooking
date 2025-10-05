import requests
import pandas as pd
import ast
from datetime import datetime, timedelta
import time
import json
from dotenv import load_dotenv
import os
import logging

load_dotenv()

class beterClient():
    def __init__(self):
        try:
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
                'username': os.getenv("BETTER_USER"),
                'password': os.getenv("BETTER_PWRD"),
            }

            response = requests.post('https://better-admin.org.uk/api/auth/customer/login', 
                                     headers=headers, 
                                     json=json_data,
                                     timeout=10)
            response.raise_for_status()
            token = json.loads(response.text)['token']
            if not token:
                raise ValueError('Token not found in response')
        except requests.exceptions.ConnectionError:
                raise Exception("Failed to connect to the API. Check your network connection.")
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise Exception("Invalid credentials. Please check username and password.")
            elif response.status_code == 403:
                raise Exception("Access forbidden.")
            else:
                raise Exception(f"HTTP error occurred: {e}")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"An error occurred: {e}")
        
        except ValueError as e:
            raise Exception(f"Error parsing response: {e}")
        
        self.auth = f'Bearer {token}'
        self.member_id = os.getenv("MEMBER_ID")
        self.logging = logging.getLogger(__name__)


    def connswaterClasses(self, date, gym, activity):
        headers = {
            'accept': 'application/json',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'authorization': self.auth,
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
        response.raise_for_status()

        sessions_text = self.cleanseResponse(response.text)
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

    def connswaterAddtoBasket(self, session_id, date):
        headers = {
            'accept': 'application/json',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'authorization': self.auth,
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
            'membership_user_id': self.member_id,
            'selected_user_id': None,
        }

        response = requests.post('https://better-admin.org.uk/api/activities/cart/add', headers=headers, json=json_data)

        return response.text


    def cleanseResponse(self, response):
        """
        Cleans the text response for processing
        """
        try:
            return response.replace('{"data":', "").replace('false', "False").replace('null', '"null"').replace('true', "True")
        except Exception as e:
            raise Exception('Error cleansing response')

    def getAvailableSlots(self, date, gym, activity):
        """
        Gets available slots for a given day
        """
        try:
            headers = {
            'accept': 'application/json',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'authorization': self.auth,
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
            response.raise_for_status()

            sessions_text = self.cleanseResponse(response.text)
            print('available slots:', sessions_text)
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
        except requests.exceptions.RequestException as e:
            raise Exception(f"An error occurred: {e}")
        
        except ValueError as e:
            raise Exception(f"Error parsing response: {e}")

    def getAvailableDates(self):
        """
        Gets all available slots for the following week
        """
        try:
            date = datetime.today() if time.strptime(datetime.now().strftime('%H:%M'), '%H:%M') < time.strptime('22:00', '%H:%M') else datetime.today() + timedelta(days=1)
            df = self.getAvailableSlots(date.strftime('%Y-%m-%d'))
            for _ in range(1, 7):
                date = date + timedelta(1)
                df = pd.concat([df, self.getAvailableSlots(date.strftime('%Y-%m-%d'))])
            return df
        except Exception as e:
            raise Exception(f"Error getting available dates, {e}")

    def checkCourts(self, date, time: int):
        """
        Given a specific datetime, check available courts and get session id
        """
        try:
            if time == 9:
                start_time = '09:00'
            else:
                start_time = str(time) + ':00'

            end_time = str(time+1) + ':00' 

            headers = {
                'authority': 'better-admin.org.uk',
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                'authorization': self.auth,
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
            response.raise_for_status()

            available_courts_text = response.text
            available_courts_text = self.cleanseResponse(available_courts_text)
            available_courts_df = pd.DataFrame(ast.literal_eval(available_courts_text[:-1]))
            available_courts_df = available_courts_df.rename(columns={'id': 'session_id'})
            available_courts_df = pd.concat([available_courts_df.drop(['location', 'name'], axis=1), available_courts_df['location'].apply(pd.Series)], axis=1)
            available_courts_df['court'] = pd.to_numeric(available_courts_df['name'].str[6])
            return available_courts_df
        except requests.exceptions.RequestException as e:
            raise Exception(f"An error occurred: {e}")
        
        except ValueError as e:
            raise Exception(f"Error parsing response: {e}")

    def addToBasket(self, session_id: int, date, time: int):
        """
        add a specified session to your basket
        """
        try:
            start_time = str(time) + ':00'
            end_time = str(time+1) + ':00'

            headers = {
                'authority': 'better-admin.org.uk',
                'accept': 'application/json',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                'authorization': self.auth,
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
                'membership_user_id': self.member_id,
                'selected_user_id': None,
            }

            response = requests.post('https://better-admin.org.uk/api/activities/cart/add', headers=headers, json=json_data)
            response.raise_for_status()

            return response.text
        except requests.exceptions.RequestException as e:
            raise Exception(f"An error occurred: {e}")
        
        except ValueError as e:
            raise Exception(f"Error parsing response: {e}")

    def checkout(self):
        """
        complete checkout on whatever is in your basket
        """
        try:
            headers = {
            'authority': 'better-admin.org.uk',
            'accept': 'application/json',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'authorization': self.auth,
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
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            raise Exception(f"An error occurred: {e}")
        
        except ValueError as e:
            raise Exception(f"Error parsing response: {e}")

    def viewBookings(self):
        try:
            headers = {
            'authority': 'better-admin.org.uk',
            'accept': 'application/json',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'authorization': self.auth,
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
            response.raise_for_status()

            bookings = self.cleanseResponse(response.text)
            bookings = pd.DataFrame(ast.literal_eval(bookings[:-1]))
            bookings['court'] = bookings['item'][0]['location']['name']
            bookings['date'] = pd.to_datetime(bookings.date)
            print('bookings:', bookings['date'])
            bookings['hour'] = pd.to_numeric(bookings.time.str.slice(0,2))
            bookings['datetime'] = bookings['date'].astype(str) + bookings['hour'].astype(str)
            bookings = bookings[['date', 'hour', 'datetime', 'court']]
            
            return bookings
        except requests.exceptions.RequestException as e:
            raise Exception(f"An error occurred: {e}")
        
        except ValueError as e:
            raise Exception(f"Error parsing response: {e}")


    if __name__ == '__main__':
        # print(connswaterClasses( 'test', #'Bearer v4.local.SAyn8MyVR9Ywe8Pvw574NM6rFBqSRYTXKXOTNdyIUQx5CwSgtvfHuvwACDo_NR1-3ngOcvYXtbUYGl4zn8Pc6PuJ79JeXx2NYOwjX-jdnGLHFj9T3cbZ_9P5RMwNVeFR2nrkeBdEJo-P5PeleWYwfiO6mKaW1k0WT-gE-XtGKYzIgOrP0PVCtTd5V8VMrZDDh3qHAVgqToCvCARlPw',
        #                         '2024-11-18',
        #                         'better-gym-connswater',
        #                         'fitness-classes-c'))
        print(connswaterAddtoBasket('Bearer v4.local.SAyn8MyVR9Ywe8Pvw574NM6rFBqSRYTXKXOTNdyIUQx5CwSgtvfHuvwACDo_NR1-3ngOcvYXtbUYGl4zn8Pc6PuJ79JeXx2NYOwjX-jdnGLHFj9T3cbZ_9P5RMwNVeFR2nrkeBdEJo-P5PeleWYwfiO6mKaW1k0WT-gE-XtGKYzIgOrP0PVCtTd5V8VMrZDDh3qHAVgqToCvCARlPw',
                                    2988951,
                                    61313807,
                                    '2024-11-11'))
