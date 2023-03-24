import requests
import json
from tqdm import tqdm
from pprint import pprint


# Создаем класс и методы для работы с API VK
class VkApi:

    URL = 'https://api.vk.com/method/'

    def __init__(self, _token):

        # Обязательные параметры запроса к API VK.
        self.required_parameters = {
                                    'access_token': _token,
                                    'v': '5.81'
                                    }

    # Метод возвращает ID пользователя "ВК", если вместо ID используется alias:
    def users_get(self, _user_id):

        _method = 'users.get'

        _url = f'{self.URL}{_method}'

        _params = {'user_ids': _user_id}

        res = requests.get(_url, params={**_params, **self.required_parameters})

        return res.json()['response'][0]['id']

    # Метод возвращает данные по фотографиям пользователя "ВК" с учетом заданных параметров запроса:
    def photo_get(self, _userID):

        # Блок проверки и преобразования ID:
        if _userID.isdigit():
            _user_id = _userID
        else:
            _user_id = self.users_get(_userID)

        # Тело метода:
        _method = 'photos.get'

        _url = f'{self.URL}{_method}'

        _params = {
            'owner_id': _user_id,
            'album_id': 'profile',
            'extended': 1,
            'count': 5
        }

        # Основной запрос метода, возвращает файл с данными в формате json для дальнейшей обработки.
        res = requests.get(_url, params={**_params, **self.required_parameters})

        return res.json()


# Создаем класс и методы для работы с API "Яндекс Диска".
class YandexDiscAPI:

    yandex_Api_URL = 'https://cloud-api.yandex.net'

    def __init__(self, _token):
        self.token = _token

    # Метод формирует обязательные заголовки параметра headers для работы с запросами к REST API "Яндекс диска".
    def get_headers(self):

        return {
                'Content-Type': 'application/json',
                'Authorization': f'OAuth {self.token}'
                }

    # Метод создает папку на "Яндекс Диске".
    def create_folder(self, _folder_name):

        _method = '/v1/disk/resources'
        _request_URL = f'{self.yandex_Api_URL}{_method}'

        _params = {'path': _folder_name}

        _headers = self.get_headers()

        res = requests.put(_request_URL, params=_params, headers=_headers)

        return res

    # Метод загрузки фотографий по URL из "ВК" на "Яндекс Диск".
    # По окончанию загрузки метод формирует лог-файл в формате json с информацией о загруженных файлах.
    def upload_photo(self, _data_file, _folder_name):

        # Формируем URL для запроса к API Яндекс Диск:
        _method = '/v1/disk/resources/upload'
        _request_URL = f'{self.yandex_Api_URL}{_method}'

        # Вызываем метод создания новой папки с указанным именем на Яндекс Диске:
        _upload_folder = self.create_folder(_folder_name)

        # Подготавливаем данные полученные со страницы пользователя "ВК" для итерации в цикле for:
        _photo_data = _data_file['response']['items']

        # Список для сбора данных о загруженных файла. Будет записан в лог-файл формата json.
        _logs_list = []

        # Рабочий список для проверки и избежания дублирования имен загружаемых файлов.
        _check_list = []

        # Основной цикл обработки информации и загрузки фотографий на "Яндекс Диск."
        for _photo in tqdm(_photo_data):

            _new_file_name = f"{_photo['likes']['count']}.jpg"
            _end_of_name = f"_{_photo['date']}"
            _download_href = _photo['sizes'][-1]['url']
            _size = _photo['sizes'][-1]['type']

            # Блок проверки дублирования имен файлов и их редактирование при совпадении:
            if _new_file_name not in _check_list:
                _download_path = f'{_folder_name}/{_new_file_name}'
                _check_list.append(_new_file_name)
            else:
                _new_file_name = f"{_photo['likes']['count']}{_end_of_name}.jpg"
                _download_path = f'{_folder_name}/{_new_file_name}'
                _check_list.append(_new_file_name)

            # Основной запрос и его параметры:
            _params = {
                        'path': _download_path,
                        'url': _download_href
                        }
            _headers = self.get_headers()

            res = requests.post(_request_URL, params=_params, headers=_headers)

            # Добавляем необходимую информацию по каждому загруженному файлу изображения:
            _logs_list.append({"file_name": _new_file_name, "size": _size})

        # Блок записи лог-файла в формате json с информацией по всем загруженным на "Яндекс Диск" файлам.
        with open('logs.json', 'w') as _f:
            json.dump(_logs_list, _f)
            print(f'\nФайл "logs.json." создан. Содержит информацию по загруженным файлам.')

        print('\nЗагрузка файлов завершена.')


# Основная логика.
# Блок 1. Работа с API VK.
if __name__ == '__main__':

    # Читаем токен ВК из файла в переменную:
    with open('.txt') as f:
        vkApiToken = f.read()

    # Инициализируем объект класса VkApi:
    Vk_response = VkApi(vkApiToken)

    # Вводим ID или alias пользователя ВК:
    userID = input('Введите ID или alias пользователя ВК: ')

    # При помощи метода класса photo_get() получаем информацию из профиля ВК и сохраняем данные в VK_photo:
    VK_photo = Vk_response.photo_get(userID)

# Блок 2. Обработка полученных данных VK_photo и работа API "Яндекс Диска".

    # Читаем токен "Яндекс Диска" из файла в переменную:
    with open('.txt') as f:
        yandexDiscToken = f.read()

    # Инициализируем объект класса YandexDiscAPI:
    YD_response = YandexDiscAPI(yandexDiscToken)

    # Вводим название каталога куда будут сохранены фотографии из ВК.
    YD_folder_name = input('Укажите имя каталога "Яндекс Диска" для сохранения фотографий: ')

    # Вызываем метод upload_photo, в результате работы которого будет создан каталог на "Яндекс Диске".
    # В данный каталог мы загрузим фотографии пользователя ВК c указанным ID.
    # По итогам загрузки будет сформирован лог-файл в формате json.
    YD_response.upload_photo(VK_photo, YD_folder_name)



