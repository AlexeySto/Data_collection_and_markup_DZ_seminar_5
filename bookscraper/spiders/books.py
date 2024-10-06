import scrapy
from bookscraper.items import BookscraperItem


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = [
        'http://books.toscrape.com/',
    ]

    def parse(self, response):
        for book in response.css('article.product_pod'):
            yield response.follow(book.css('h3 a::attr(href)').get(), self.parse_book)

        # Переход на следующую страницу
        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_book(self, response):
        title = response.css('div.product_main h1::text').get()
        price = response.css('p.price_color::text').get()
        availability = response.css('p.availability::text').getall()
        rating = response.css('p.star-rating::attr(class)')
        description = response.css('div#product_description ~ p::text').get()
        
        yield BookscraperItem(title=title, price=price, availability=availability, rating=rating, description=description)
        