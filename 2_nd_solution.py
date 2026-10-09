import socket
import re
import urllib.parse
from bs4 import BeautifulSoup

HOST = "hw1.alexbers.com"
MY_COOKIE = "1356f7fb9f5e42fea896c2c260f8df15"
URL = "http://hw1.alexbers.com"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, 80))
request = f"GET /path HTTP/1.1\r\nHost: {HOST}\r\nCookie: user={MY_COOKIE}; path=/\r\nConnection: close\r\n\r\n"
s.send(request.encode('utf-8'))

response_bytes = b""
while True:
    msg = s.recv(1024)
    if len(msg)<=0:
        break
    response_bytes += msg

s.close()

normal_text = response_bytes.decode('utf-8')
headers, html_body = normal_text.split('\r\n\r\n', 1)

while True:
    soup = BeautifulSoup(html_body, "html.parser")
    print(soup.get_text(separator="\n", strip=True))

    if "Шаг" not in html_body:
        print(soup.get_text(separator="\n", strip=True))
        break

    new_headers = {}
    new_cookies = {"user": MY_COOKIE}
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

    next_url = URL + new_address


    s_params = ""
    if len(new_params) != 0:
        s_params = "?" + urllib.parse.urlencode(new_params)

    s_headers = ""
    if len(new_headers) != 0:
        for key, value in new_headers.items():
            s_headers += f"{key}: {value}\r\n"

    s_cookies = ""
    if len(new_cookies) != 0:
        arr_cookies = []
        for key, value in new_cookies.items():
            arr_cookies.append(f"{key}={value}")
        s_cookies = "Cookie: " + "; ".join(arr_cookies) + "\r\n"

    s_data = ""
    arr_data = []
    if len(new_data) != 0:
        for key, value in new_data.items():
            arr_data.append(f"{key}={value}")
        s_data = "&".join(arr_data)

    if len(new_files) != 0:
        for key, (file_name, file_link) in new_files.items():
            arr_data.append(f"name={file_name}")
            arr_data.append(f"link={file_link}")

    s_data = "&".join(arr_data)

    is_post = False
    if new_files or new_data or soup.find(string=re.compile("POST-запрос", re.IGNORECASE)):
        is_post = True

    if is_post:
        if len(new_files) != 0:
            boundary = "--IDidNotHaveFantasy07824977"
            body_bytes = b""

            for key, value in new_data.items():
                body_bytes += f"--{boundary}\r\n".encode('utf-8')
                body_bytes += f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode('utf-8')
                body_bytes += f"{value}\r\n".encode('utf-8')

            for key, (file_name, file_content) in new_files.items():
                body_bytes += f"--{boundary}\r\n".encode('utf-8')
                body_bytes += f'Content-Disposition: form-data; name="{file_name}"; filename="{file_name}"\r\n'.encode(
                    'utf-8')
                body_bytes += b'Content-Type: application/octet-stream\r\n\r\n'
                body_bytes += file_content.encode('utf-8') + b'\r\n'

            body_bytes += f"--{boundary}--\r\n".encode('utf-8')

            request_head = (
                f"POST {new_address} HTTP/1.1\r\n"
                f"Host: {HOST}\r\n"
                f"{s_headers}"
                f"{s_cookies}"
                f"Content-Type: multipart/form-data; boundary={boundary}\r\n"
                f"Content-Length: {len(body_bytes)}\r\n"
                f"Connection: close\r\n"
                f"\r\n"
            ).encode('utf-8')

            request_to_send = request_head + body_bytes

        else:
            s_data = ""
            if len(new_data) != 0:
                s_data = urllib.parse.urlencode(new_data)

            data_len = len(s_data.encode('utf-8'))
            request_to_send = (
                f"POST {new_address} HTTP/1.1\r\n"
                f"Host: {HOST}\r\n"
                f"{s_headers}"
                f"{s_cookies}"
                f"Content-Type: application/x-www-form-urlencoded\r\n"
                f"Content-Length: {data_len}\r\n"
                f"Connection: close\r\n"
                f"\r\n"
                f"{s_data}"
            ).encode('utf-8')

    else:
        full_path = new_address + s_params
        request_to_send = (
            f"GET {full_path} HTTP/1.1\r\n"
            f"Host: {HOST}\r\n"
            f"{s_headers}"
            f"{s_cookies}"
            f"Connection: close\r\n"
            f"\r\n"
        ).encode('utf-8')

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, 80))

    s.sendall(request_to_send)

    response_bytes = b""
    while True:
        msg = s.recv(4096)
        if not msg:
            break
        response_bytes += msg

    s.close()

    normal_text = response_bytes.decode('utf-8', errors='ignore')
    if "\r\n\r\n" in normal_text:
        headers, html_body = normal_text.split('\r\n\r\n', 1)
    else:
        headers, html_body = normal_text, ""