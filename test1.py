from requests import delete, put, get


print(get('http://127.0.0.1:8008/api/user').json())
