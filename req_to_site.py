import json
import requests
from auth_data import keyAPI


def fst_request_for_destination_id(city: str):
    '''
    Функция запроса для получения id места назначения.

    :param city: str - город назначения
    :return: None
    '''

    querystring = {"query": city, "locale": "en_US", "currency": "USD"}
    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': f'{keyAPI}'
    }
    try:
        fst_req = requests.get('https://hotels4.p.rapidapi.com/locations/v2/search',
                               headers=headers, params=querystring)
        fst_req_data = json.loads(fst_req.text)
    except (BrokenPipeError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError):
        return 'Ошибка при получении запроса.'
    return fst_req_data['suggestions'][0]['entities'][0]['destinationId']


def sec_request_for_hotel_info(destination_id: str, check_in: str = '2022-05-09', check_out: str = '2022-06-12'):
    '''
    Функция API запроса для получение полной информации об отелях с учётом параметров.

    :param destination_id: str - id места назначения
    :param check_in: str - дата заезда в формате год-месяц-дата
    :param check_out: str - дата выезда в формате год-месяц-дата
    :return: None
    '''

    querystring = {"destinationId": destination_id, "pageNumber": "1", "pageSize": "25", "checkIn": check_in,
                   "checkOut": check_out, "adults1": "1", "sortOrder": "PRICE", "locale": "en_US", "currency": "USD"}
    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': f'{keyAPI}'
    }

    try:
        sec_req = requests.get('https://hotels4.p.rapidapi.com/properties/list', headers=headers, params=querystring)
        sec_req_data = json.loads(sec_req.text)
    except (BrokenPipeError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError):
        return 'Ошибка при получении запроса.'
    return sec_req_data['data']['body']['searchResults']['results']


def third_request_for_hotels_photo(hotel_id: str, num_hot_photo: int):
    '''
    Функция API запроса для получения фото отеля.

    :param hotel_id: str -  id отеля
    :return: None
    '''

    querystring = {"id": hotel_id}
    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': f'{keyAPI}'
    }
    try:
        third_req = requests.get("https://hotels4.p.rapidapi.com/properties/get-hotel-photos", headers=headers, params=querystring)
        third_req_data = json.loads(third_req.text)
        hot_photo_lst = third_req_data['hotelImages']
    except Exception:
        return ['Запрос по получению фото отеля получил ошибку.']

    try:
        photo_url_lst = []
        for i_num in range(num_hot_photo):
            hot_photo_url = hot_photo_lst[i_num]['baseUrl'].format(size='y')
            photo_url_lst.append(hot_photo_url)
        return photo_url_lst
    except IndexError:
        photo_url_lst.append('Столько фото отеля нет.')
        return photo_url_lst
