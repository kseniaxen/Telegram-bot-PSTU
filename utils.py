import json
import csv
from typing import Dict, Any

def load_texts(file_path="text.json"):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def load_case_data(file_path: str = 'data/data.csv') -> Dict[str, Any]:
    """Загружает данные из CSV файла и возвращает словарь с кэшированными данными"""
    data = {}
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                data[row['УникальныйКод']] = {
                    'ФизическоеЛицо': row['ФизическоеЛицо'],
                    'УникальныйКод': row['УникальныйКод']
                }
        return data
    except FileNotFoundError:
        raise Exception(f"Файл {file_path} не найден")
    except Exception as e:
        raise Exception(f"Ошибка при загрузке данных: {str(e)}")

# Глобальная переменная с загруженными данными
CASE_DATA = load_case_data()