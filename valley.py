import bs4
import requests
import pandas as pd
import json
from datetime import datetime, timedelta

def getAvailableSlots():
    date = datetime.today().strftime('%Y-%m-%d')
    end_date = datetime.strptime(date, '%Y-%m-%d') + timedelta(days=10)
    end_date = str(end_date.strftime('%Y-%m-%d'))

    headers = {
        'authority': 'antrimandnewtownabbey.legendonlineservices.co.uk',
        'accept': '*/*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://antrimandnewtownabbey.legendonlineservices.co.uk',
        'referer': 'https://antrimandnewtownabbey.legendonlineservices.co.uk/valley/bookingscentre/membertimetable',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'ResourceSubTypeIdList': ['70', '72'],
        'FacilityLocationIdList': '1917',
        'DateFrom': date + 'T00:00:00+00:00',
        'DateTo': end_date + 'T00:00:00+00:00',
    }

    with requests.Session() as session:
        username = 'adamu_1996@hotmail.com'
        password = 'Jordanstown-125'
        session.auth = (username, password)
        response = session.post(
            'https://antrimandnewtownabbey.legendonlineservices.co.uk/valley/Timetable/GetClassTimeTable',
            headers=headers,
            data=data,
        )

    response_json = json.loads(response.text)
    return pd.json_normalize(response_json['Results'])

def login(session):
    headers = {
        'authority': 'antrimandnewtownabbey.legendonlineservices.co.uk',
        'accept': '*/*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        # 'cookie': '_ga=GA1.1.1853859787.1707825498; ASP.NET_SessionId=qs0mbg442ak1jv1ulo3sbnlq; __HOST-samesite=CD4CB77E0D6F64AA1F8B832E01B7A73B04EE347CFE28B11628C511FE707B8095; UserLanguage=%7b%22Id%22%3a23%2c%22LanguageCode%22%3a%22en%22%2c%22NativeName%22%3a%22English%22%2c%22DefaultCulture%22%3a%22gb%22%7d; Responsive=1; __RequestVerificationToken=VdD2BZf33knj53CKXuipUQr6VebU40ZP1gLVHipwXI-j41pmTQyTX9FvQpZCkPhXEmLrJWPkD-aJUQ6ng8sUYivQ3rY1; LegendAffinity=71a34d91b0026fb721b94a338d3637c22fb782f3d696b0c11237d4c26a5484f5; LanguageToggle=false; NoticesChecked=true; _ga_0Y5R9WGBC0=GS1.1.1709618497.10.1.1709618698.0.0.0',
        'origin': 'https://antrimandnewtownabbey.legendonlineservices.co.uk',
        'referer': 'https://antrimandnewtownabbey.legendonlineservices.co.uk/valley/account/login',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'login.email': 'jillmcc09@gmail.com',
        'login.password': 'Standrews1',
        'login.RedirectURL': '',
    }

    response = session.post(
        'https://antrimandnewtownabbey.legendonlineservices.co.uk/valley/account/processloginrequest',
        headers=headers,
        data=data,
    )

    return response.cookies

def viewBookings():
    session = requests.Session()
    login(session)
    headers = {
        'authority': 'antrimandnewtownabbey.legendonlineservices.co.uk',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'content-type': 'application/json;charset=utf-8',
        # 'cookie': '_ga=GA1.1.1853859787.1707825498; ASP.NET_SessionId=qs0mbg442ak1jv1ulo3sbnlq; __HOST-samesite=CD4CB77E0D6F64AA1F8B832E01B7A73B04EE347CFE28B11628C511FE707B8095; UserLanguage=%7b%22Id%22%3a23%2c%22LanguageCode%22%3a%22en%22%2c%22NativeName%22%3a%22English%22%2c%22DefaultCulture%22%3a%22gb%22%7d; Responsive=1; __RequestVerificationToken=VdD2BZf33knj53CKXuipUQr6VebU40ZP1gLVHipwXI-j41pmTQyTX9FvQpZCkPhXEmLrJWPkD-aJUQ6ng8sUYivQ3rY1; LegendAffinity=71a34d91b0026fb721b94a338d3637c22fb782f3d696b0c11237d4c26a5484f5; LanguageToggle=false; LEGEND_SessionCacheToken=hzze5hgiohoba0l0f5puu4ys; NoticesChecked=true; _ga_0Y5R9WGBC0=GS1.1.1709618497.10.1.1709620068.0.0.0',
        'referer': 'https://antrimandnewtownabbey.legendonlineservices.co.uk/valley/viewbookings',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    params = {
        'contactId': '',
        '_': '1709620069153',
    }

    response = session.get(
        'https://antrimandnewtownabbey.legendonlineservices.co.uk/valley/viewbookings/contactSportsHallbookings',
        params=params,
        headers=headers,
    )
    print(response)
    print(response.text)

if __name__ == '__main__':
    viewBookings()

         
