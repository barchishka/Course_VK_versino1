import json
import time
import requests
from progress.bar import FillingSquaresBar

token_vk = '...'
token_ya = '...'
test_vk_id = '...'


def creation_json(info):
    with open('info_photo_files.json', 'w') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)


class YaUploader:
    def __init__(self):
        self.token_vk = token_vk
        self.token_ya = token_ya
        self.user_id = test_vk_id
        self.yandex_folder = input('Укажите название папки на Яндекс.Диске: ')
        self.count_save = int(input('Введите максимальное число сохраняемых фотографий (5 по умолчанию): '))

    def get_new_folder(self):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token_ya}'
        }
        params = {'path': self.yandex_folder}
        response = requests.put(url=url, headers=headers, params=params)
        if response.status_code != 201:
            return f'Папка с именем: {self.yandex_folder} уже существует!'
        else:
            return f'Папка: {self.yandex_folder} создана на Yandex disc'

    def get_requests_vk(self):
        url = "https://api.vk.com/method/photos.get?"
        params = {
            'owner_id': self.user_id,
            'album_id': 'wall',
            'extended': 1,
            'photo_sizes': 1,
            'access_token': self.token_vk,
            'v': '5.131'
        }
        response = requests.get(url=url, params=params)
        if response.status_code != 200:
            print('Failed')
        return response.json()

    def upload_file_ya_disk(self, file_name, url_vk):
        self.get_new_folder()
        file_path = self.yandex_folder + '/' + file_name
        up_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {self.token_ya}'}
        params = {'url': url_vk, 'path': file_path}
        response = requests.post(url=up_url, headers=headers, params=params)
        response.raise_for_status()
        if response.status_code == 202:
            print(f'\n Файл {file_name} загружен на Яндекс Диск')

    def get_response(self):
        count = 0
        if 'error' in self.get_requests_vk():
            print(f'Ошибка: Аккаунт ID:{self.user_id} недоступен')
        elif self.get_requests_vk()['response'].get('count', False) == 0:
            print(f'На аккаунте ID {self.user_id} нет фотографий!')
        else:
            info_list = []
            final_list = []
            for i in self.get_requests_vk()['response']['items']:
                if count < self.count_save:
                    temp_dict = {'file_name': f"{str(i['likes']['count'])}" + '.jpg',
                                 'size': f"{i['sizes'][-1]['type']}"}
                    file_name = f"{str(i['likes']['count'])}" + '.jpg'
                    if file_name not in info_list:
                        file_name = file_name
                        info_list.append(file_name)
                        final_list.append(temp_dict)
                        self.upload_file_ya_disk(file_name, f"{i['sizes'][-1]['url']}")
                        count += 1
                        print(file_name)
                    else:
                        alter_dict = {'file_name': f"{str(i['likes']['count'])}" + f"({str(i['date'])})" + '.jpg',
                                      'size': f"{i['sizes'][-1]['type']}"}
                        file_name = f"{str(i['likes']['count'])}" + f"({str(i['date'])})" + '.jpg'
                        info_list.append(file_name)
                        final_list.append(alter_dict)
                        self.upload_file_ya_disk(file_name, f"{i['sizes'][-1]['url']}")
                        count += 1
                        print(file_name)
            creation_json(final_list)

    def start(self):
        if self.count_save is not None:
            bar = FillingSquaresBar('Countdown', max=self.count_save)
            for number in range(self.count_save):
                bar.next()
                time.sleep(1)
            self.get_response()
            bar.finish()
        else:
            self.count_save = 5
            bar = FillingSquaresBar('Countdown', max=self.count_save)
            for number in range(5):
                bar.next()
                time.sleep(1)
            self.get_response()
            bar.finish()


if __name__ == '__main__':
    uploader = YaUploader()
    uploader.start()
