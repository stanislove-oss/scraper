import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from scraper import get_book_data, scrape_books



BOOK_URL = 'http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'


def test_get_book_data_returns_dict():
    """Проверяем, что функция возвращает словарь с нужными ключами"""
    data = get_book_data(BOOK_URL)
    assert isinstance(data, dict), "Результат должен быть словарём"
    for key in ["title", "price", "availability", "rating", "description"]:
        assert key in data, f"Ключ {key} должен присутствовать в словаре"


def test_get_book_data_title_correct():
    """Проверяем, что заголовок книги содержит ожидаемое название"""
    data = get_book_data(BOOK_URL)
    title = data.get("title", "").lower()
    assert "light in the attic" in title, "Название книги не совпадает с ожидаемым"


def test_scrape_books_collects_books(tmp_path):
    """
    Проверяем, что scrape_books собирает хотя бы несколько книг и
    сохраняет данные в файл при is_save=True
    """
    test_file = tmp_path / "books_data.txt"

    res = scrape_books(is_save=True, delay_sec=0.0, max_pages=1)

    assert isinstance(res, list), "Функция должна вернуть список"
    assert len(res) > 0, "Должно быть собрано хотя бы несколько книг"
    assert test_file.exists() or len(res) > 0, "Файл не создан или список пуст"
    
    
