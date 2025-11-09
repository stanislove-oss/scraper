import time
import requests
import schedule
from bs4 import BeautifulSoup


def get_book_data(book_url: str) -> dict:
    """
    Извлекает информацию о книге с сайта Books to Scrape.
    
    Параметры
    ----------
    book_url : str
        Ссылка на страницу конкретной книги

    Возвращает
    ----------
    dict
        Словарь с данными: название, цена, рейтинг, наличие, описание,
        ссылка на изображение и характеристики из таблицы Product Information.
    """


    response = requests.get(book_url)
    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.find("div", class_="product_main").find("h1").text.strip()

    price = soup.find("p", class_="price_color").text.strip()

    availability = soup.find("p", class_="instock availability").text.strip()

    rating_tag = soup.find("p", class_="star-rating")
    rating = None
    if rating_tag:
        for cls in rating_tag["class"]:
            if cls in ["One", "Two", "Three", "Four", "Five"]:
                rating = cls
                break

    description = None
    desc_header = soup.find("div", id="product_description")
    if desc_header:
        desc_paragraph = desc_header.find_next("p")
        if desc_paragraph:
            description = desc_paragraph.text.strip()

    image_tag = soup.find("div", class_="item active").find("img")
    image_url = "http://books.toscrape.com/" + image_tag["src"].replace("../", "")

    table = soup.find("table", class_="table table-striped")
    product_info = {}
    if table:
        for row in table.find_all("tr"):
            key = row.find("th").text.strip()
            value = row.find("td").text.strip()
            product_info[key] = value

    return {
        "title": title,
        "price": price,
        "availability": availability,
        "rating": rating,
        "description": description,
        "image_url": image_url,
        "product_info": product_info
    }

BASE = "http://books.toscrape.com"
CATALOGUE = f"{BASE}/catalogue/" 
    
def _make_abs_book_url(href: str) -> str:
    """
    Преобразует относительный href с каталожной страницы в абсолютный URL книги.
    Без urllib.parse: просто аккуратно склеиваем строки.
    """
    if href.startswith("http://") or href.startswith("https://"):
        return href
    href = href.lstrip("/")
    while href.startswith("../"):
        href = href[3:]
    return CATALOGUE + href

def scrape_books(is_save: bool = False, delay_sec: float = 0.0, max_pages: int = 1) -> list:
    """
    Обходит все страницы каталога Books to Scrape и собирает данные о всех книгах.

    Параметры
    ----------
    is_save : bool, optional
        Если True — сохраняет результат в файл `books_data.txt` (по 1 книге на строку).
        По умолчанию False.
    delay_sec : float, optional
        Пауза между запросами к страницам/книгам (в секундах) для вежливого скрейпинга.
        По умолчанию 0.0.
    max_pages: int, optional
        Максимальное количество страниц, которые надо просмотреть

    Возвращает
    ----------
    list
        Список словарей, каждый словарь — результат `get_book_data()` для одной книги.
    """

    all_books = []
    page_num = 1

    while page_num <= max_pages:
        page_url = f"{CATALOGUE}page-{page_num}.html"
        resp = requests.get(page_url)
        if resp.status_code != 200:
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        pods = soup.select("article.product_pod h3 a")
        if not pods:
            break

        book_urls = [_make_abs_book_url(a.get("href", "")) for a in pods]

        for burl in book_urls:
            try:
                data = get_book_data(burl)
                all_books.append(data)
            except Exception:
                continue
            if delay_sec:
                time.sleep(delay_sec)

        page_num += 1
        if delay_sec:
            time.sleep(delay_sec)

    if is_save:
        with open("./artifacts/books_data.txt", "w", encoding="utf-8") as f:
            for item in all_books:
                f.write(str(item) + "\n")

    return all_books


def job():
    try:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Старт сбора…")
        res = scrape_books(is_save=True, delay_sec=0.0)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Готово: собрано {len(res)} книг.")
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Ошибка: {e}")

schedule.every().day.at("19:00").do(job)

if __name__ == '__main__':
    schedule.run_pending()
    time.sleep(30)
    
