# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from pymongo import MongoClient
import re
import csv
import json


class BookscraperPipeline:
    def open_spider(self, spider):
        # Настройки для сохранения в CSV
        self.csv_file = open(f"{spider.name}.csv", "w", newline="", encoding="utf-8")
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['title', 'price', 'availability', 'rating', 'description'])

        # Настройки для сохранения в JSON
        self.json_file = open(f"{spider.name}.json", "w", encoding="utf-8")
        self.json_data = []

        # Настройка MongoDB
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client[spider.name]

    def close_spider(self, spider):
        # Закрытие CSV файла
        self.csv_file.close()
        
        # Сохранение данных в JSON файл
        json.dump(self.json_data, self.json_file, indent=4, ensure_ascii=False)
        self.json_file.close()

        # Закрытие соединения с MongoDB
        self.client.close()

    def get_rating(self, response):
        ratings = {
            'One': 1,
            'Two': 2,
            'Three': 3,
            'Four': 4,
            'Five': 5
        }
        rating_text = response.re_first('star-rating (\w+)')
        return ratings.get(rating_text, 0)
    
    def extract_number(self, response):
        # Ищем в строке все цифры, а затем конвертируем в целое число
        match = re.search(r'\d+', ''.join(response).strip().replace('\n', ''))
        if match:
            return int(match.group())
        return None  # Вернуть None, если число не найдено
    
    def process_item(self, item, spider):
        item['price'] = float(item.get('price')[2:])
        item['availability'] = self.extract_number(item.get('availability'))
        item['rating'] = self.get_rating(item.get('rating'))
        
        # Сохранение данных в CSV
        self.csv_writer.writerow([item['title'], item['price'], item['availability'], item['rating'], item['description']])

        # Сохранение данных в JSON
        self.json_data.append(dict(item))

        # Сохранение данных в MongoDB
        self.db.books.insert_one(dict(item))
        
        return item
    