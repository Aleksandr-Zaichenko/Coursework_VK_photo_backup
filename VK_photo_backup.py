import requests
import json
from tqdm import tqdm
import datetime

vk_token = 'токен ВК'
user_id = 'id пользователя vk'
ya_tok = 'OAuth токен с Полигона Яндекс.Диска'

# Получать фотографии с профиля. Для этого нужно использовать метод photos.get.
# Пользователь вводит: id пользователя vk; токен с Полигона Яндекс.Диска;

class SocNetClient:
    VK_BASE_URL = 'https://api.vk.com/method/'
    YA_URL_BASE = 'https://cloud-api.yandex.net'
    
    def __init__(self, vk_user_id, yandex_token, album_name='profile', quantity_photo=5):
        self.yandex_token = yandex_token
        self.vk_user_id = vk_user_id
        self.album_name = album_name
        self.quantity_photo = quantity_photo    
    
    def get_profile_photos(self):
        params = {'access_token': vk_token, 'v': '5.131', 
            'owner_id': self.vk_user_id, 'album_id': self.album_name, 
            'extended': 1, 'count': self.quantity_photo
        }
        response = requests.get(f'{self.VK_BASE_URL}photos.get', params=params)
        return response.json()
        
    def get_likes_list(self):
        likes_list = []
        photos_info = self.get_profile_photos()
        for item in photos_info['response']['items']:
            likes_list.append(item['likes']['count'])
        return likes_list    

# Для имени фотографий использовать количество лайков, если количество лайков одинаково, то добавить дату загрузки.
    
    def get_max_size(self):
        photos_dict = {}
        photos_info = self.get_profile_photos()
        check_likes = self.get_likes_list()
        for item in photos_info['response']['items']:
            for photo in item['sizes']:
                if photo['type'] == 'w':
                    if check_likes.count(item['likes']['count']) > 1:
                        photos_dict.setdefault(f"{item['likes']['count']}_{item['date']}", photo['url'])
                    else:
                        photos_dict.setdefault(item['likes']['count'], photo['url'])
        return photos_dict                
        
# Сохранять фотографии максимального размера(ширина/высота в пикселях) на Я.Диске.
# Использовать REST API Я.Диска и ключ, полученный с полигона.
# Для загруженных фотографий нужно создать свою папку.
# Сохранять указанное количество фотографий(по умолчанию 5) наибольшего размера (ширина/высота в пикселях) на Я.Диске
# Сделать прогресс-бар или логирование для отслеживания процесса программы.
# Сохранять информацию по фотографиям в json-файл с результатами.

    def create_ya_dir(self):
        current_time = str(datetime.datetime.now().time()).split('.')[0]
        current_time = current_time.replace(':', '_')
        url_create_dir = f'{self.YA_URL_BASE}/v1/disk/resources'
        params = {'path': f'{self.album_name}_{current_time}'}
        headers = {'Authorization': self.yandex_token}
        response = requests.put(url_create_dir, params=params, headers=headers)
        return current_time
    
    def ya_cloud_save(self):
        max_size_photos = self.get_max_size()
        mk_dir = self.create_ya_dir()
        photos_data = []
        for img_name, img_url in tqdm(max_size_photos.items()):        
            url_image = img_url
            image_name = img_name
            url_for_upload = f'{self.YA_URL_BASE}/v1/disk/resources/upload'
            params = {'url': url_image, 'path': f'{self.album_name}_{mk_dir}/{image_name}'}
            headers = {'Authorization': self.yandex_token}
            response = requests.post(url_for_upload, params=params, headers=headers)
            photos_data.append({"file_name": image_name, "size": "w"})
        with open('photos_data.json', 'w') as file:
            json.dump(photos_data, file)    
        

if __name__ == '__main__':
    vk_client = SocNetClient(user_id, ya_tok)
    vk_client.ya_cloud_save()