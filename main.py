import requests
from lxml import html
import json


def first_site():
    url = "https://www.mebelshara.ru/contacts"
    converted_lat, converted_lon, parsed_data, phones_list = [], [], [], []

    r = requests.get(url)
    t = html.fromstring(r.content)
    print(r.status_code)
    lat = t.xpath("//div/@data-shop-latitude")
    lon = t.xpath("//div/@data-shop-longitude")
    for i in range(len(lat)):
        converted_lat.append(float(lat[i]))
        converted_lon.append(float(lon[i]))
    latlon = list(zip(converted_lat, converted_lon))
    name = t.xpath("//div[@class='shop-name']/text()")
    address = t.xpath("//div[@class='shop-address']/text()")
    shop_weekends = t.xpath("//div[@class='shop-weekends']/text()")
    sliced_shop_weekends = [i[14::] for i in shop_weekends]

    shop_work_time = t.xpath("//div[@class='shop-work-time']/text()")
    working_hours = list(zip(shop_work_time, sliced_shop_weekends))
    phones = t.xpath("//div[@class='shop-list-item']/@data-shop-phone")
    phones_list = [item.split(', ') for item in phones]

    for i in range(len(name)):
        parsed_data.append({
            "address": address[i],
            "latlon": latlon[i],
            "name": name[i],
            "phones": phones_list[i],
            "working_hours": working_hours[i]
        })
    print("first site done!")
    return parsed_data


def second_site():
    url = "https://www.tui.ru/api/office/list/?cityId=1&subwayId=&hoursFrom=&hoursTo=&serviceIds=all" \
          "&toBeOpenOnHolidays=false "

    response = json.loads(requests.get(url).content)
    parsed_data, name, address, phone, \
    raw_phone_number, formatted_phone_number, \
    latitude, longitude, weekdays, monday_friday, saturday, sunday = [], [], [], [], [], [], [], [], [], [], [], []

    for r in response:
        name.append(r['name'])
        address.append(r['address'])
        phone.append(r['phones'])
        latitude.append(r['latitude'])
        longitude.append(r['longitude'])
        latlon = list(zip(latitude, longitude))
        weekdays.append(r['hoursOfOperation'])

    for day in weekdays:
        if not day['sunday']['isDayOff']:
            weekend_sunday = f"вс - {day['sunday']['startStr']} до {day['sunday']['endStr']}"
            sunday.append(weekend_sunday)
        elif day['sunday']['isDayOff']:
            weekend_sunday = "вс - выходной"
            sunday.append(weekend_sunday)

        workdays = f"пн - пт {day['workdays']['startStr']} до {day['workdays']['endStr']}"
        monday_friday.append(workdays)

        if not day['saturday']['isDayOff']:
            weekend_saturday = f"cб - {day['saturday']['startStr']} до {day['saturday']['endStr']}"
            saturday.append(weekend_saturday)
        elif day['saturday']['isDayOff']:
            weekend_saturday = "сб - выходной"
            saturday.append(weekend_saturday)

    working_hours = list(zip(monday_friday, saturday, sunday))
    for item in phone:
        raw_phone_list = [i['phone'] for i in item]
        formatted_phone_list = [item.replace(u'\xa0', u' ').replace('  ', u'')
                                for item in raw_phone_list if item != '']
        formatted_phone_number.append(formatted_phone_list)
    for i in range(len(weekdays)):
        parsed_data.append({
            "address": address[i],
            "latlon": latlon[i],
            "name": name[i],
            "phones": formatted_phone_number[i],
            "working_hours": working_hours[i]
        })
    print('second site done!')
    return parsed_data


def main():
    first_site_data_list = first_site()
    second_site_site_data_list = second_site()
    result_json = [first_site_data_list, second_site_site_data_list]
    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(result_json, f, ensure_ascii=False, indent=3)


if __name__ == '__main__':
    main()
