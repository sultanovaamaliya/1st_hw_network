import requests
from bs4 import BeautifulSoup
import re

session = requests.Session()
session.cookies.set("user", "1356f7fb9f5e42fea896c2c260f8df15")
url = "http://hw1.alexbers.com"

response = session.get(url)

while True:
    soup = BeautifulSoup(response.text, "html.parser")

    if "Шаг" not in response.text:
        print(soup.get_text(separator="\n", strip=True))
        break

    new_headers = {}
    new_cookies = {}
    new_files = {}
    new_params = {}
    new_data = {}
    new_address = ""

    headers_text = soup.find(string=re.compile("заголовки", re.IGNORECASE))
    if headers_text:
        headers_table = headers_text.find_next("table")
        rows = headers_table.find_all('tr')[1:]
        for row in rows:
            cols = row.find_all('td')
            key = cols[0].get_text(strip=True)
            value = cols[1].get_text(strip=True)
            new_headers[key] = value


    cookie_text = soup.find(string=re.compile("cookie", re.IGNORECASE))
    if cookie_text:
        cookies_table = cookie_text.find_next("table")
        rows = cookies_table.find_all('tr')[1:]
        for row in rows:
            cols = row.find_all('td')
            key = cols[0].get_text(strip=True)
            value = cols[1].get_text(strip=True)
            new_cookies[key] = value


    files_text = soup.find(string=re.compile("загрузите", re.IGNORECASE))
    if files_text:
        files_table = files_text.find_next("table")
        rows = files_table.find_all("tr")[1:]
        for i, row in enumerate(rows):
            cols = row.find_all('td')
            key = cols[0].get_text(strip=True)
            value = cols[1].get_text(strip=True)
            new_files[key] = (key, value)


    params_text = soup.find(string=re.compile("параметры", re.IGNORECASE))
    if params_text:
        params_table = params_text.find_next("table")
        rows = params_table.find_all('tr')[1:]
        for row in rows:
            cols = row.find_all('td')
            new_params[cols[0].get_text(strip=True)] = cols[1].get_text(strip=True)


    forms_text = soup.find(string=re.compile("данные формы", re.IGNORECASE))
    if forms_text:
        form_table = forms_text.find_next("table")
        rows = form_table.find_all('tr')[1:]
        for row in rows:
            cols = row.find_all('td')
            new_data[cols[0].get_text(strip=True)] = cols[1].get_text(strip=True)


    code_tags = soup.find_all('code')
    for code in code_tags:
        text = code.get_text(strip=True)
        if text.startswith('/'):
            new_address = text
            break

    if not new_address:
        link_tag = soup.find('a')
        if link_tag and link_tag.get('href') and not link_tag['href'].startswith('http'):
            new_address = link_tag['href']

    if not new_address:
        match = re.search(r"(/[\w\d]+)", soup.text)
        if match:
            new_address = match.group(1)

    next_url = url + new_address

    kwargs = {}
    if new_headers: kwargs['headers'] = new_headers
    if new_cookies: kwargs['cookies'] = new_cookies
    if new_files: kwargs['files'] = new_files
    if new_params: kwargs['params'] = new_params
    if new_data: kwargs['data'] = new_data

    is_post = False
    if new_files or new_data or soup.find(string=re.compile("POST-запрос", re.IGNORECASE)):
        is_post = True

    if is_post:
        next_response = session.post(next_url, **kwargs)
    else:
        next_response = session.get(next_url, **kwargs)
    response = next_response
    print(response.text)