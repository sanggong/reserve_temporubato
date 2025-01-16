import datetime
from bs4 import BeautifulSoup
import requests
from dateutil.relativedelta import relativedelta

from send_discord import discord_send_message


def main():
    header = {"User-gent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"}
    response = requests.get("http://decoder.kr/book-rubato/?ckattempt=1", headers=header)
    print(response.text)

    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        div_tag = soup.select_one('div.ab-booking-form')
        form_id = div_tag.get('data-form_id') 

        header = {
            "Cookie": f"{response.headers['Set-Cookie'].split(';')[0]};"
        }

        response = requests.get(f"http://decoder.kr/wp-admin/admin-ajax.php?action=ab_render_time&form_id={form_id}&time_zone_offset=-540", headers=header)
        
        not_reserved = []
        data = response.json()
        not_reserved.extend(find_not_reserved_in_month(data["slots"]))

        start_date = datetime.datetime(data["date_min"][0], data["date_min"][1]+1, data["date_min"][2]) + relativedelta(months=1)
        end_date = datetime.datetime(data["date_max"][0], data["date_max"][1]+1, data["date_max"][2])

        current_date = start_date
        while current_date.month <= end_date.month:
            response = requests.get(f"http://decoder.kr/wp-admin/admin-ajax.php?action=ab_render_time&form_id={form_id}&selected_date={current_date.strftime('%Y-%m-%d')}&cart_key=0", headers=header)
            data = response.json()

            not_reserved.extend(find_not_reserved_in_month(data["slots"]))
            current_date += relativedelta(months=1)   # 한 달 간격으로 증가
        
        print(f"not_reserved: {not_reserved}")
        if not_reserved:
            discord_send_message(not_reserved)


def find_not_reserved_in_month(reserve_month_info):
    result = []
    for info in reserve_month_info:
        result.extend(find_not_reserved_in_day(info))
    return result


def find_not_reserved_in_day(reserve_day_info):
    soup = BeautifulSoup(reserve_day_info, 'html.parser')
    div_tag = soup.select('button.ab-available-hour')

    if len(div_tag) >= 1:
        not_reserved = filter(lambda x: ("ab-available-hour" in x) and ('disabled="disabled"' not in x) , str(div_tag[0]).split("/button&gt;"))
        return list(not_reserved)
    
    return []


if __name__=="__main__":
    main()