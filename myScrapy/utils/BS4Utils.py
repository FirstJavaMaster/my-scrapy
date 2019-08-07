from bs4 import BeautifulSoup


def get_soup(response):
    return BeautifulSoup(response.body, 'lxml')
