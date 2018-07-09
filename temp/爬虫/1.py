import requests
from bs4 import BeautifulSoup

response = requests.get("http://8080.net")
print(response.cookies)

soup = BeautifulSoup(response.text, 'html.parser')
new_list = soup.find_all(name='p')
print(new_list)
