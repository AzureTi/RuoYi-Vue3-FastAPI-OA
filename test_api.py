import requests

base_url = 'http://127.0.0.1:9099'

captcha_response = requests.get(f'{base_url}/captchaImage')
print('Captcha response:', captcha_response.json())

uuid = captcha_response.json().get('uuid')
print('UUID:', uuid)

login_url = f'{base_url}/login'
login_data = {
    'username': 'admin',
    'password': 'admin123',
    'code': '',
    'uuid': uuid
}

response = requests.post(login_url, data=login_data)
print('Login response:', response.json())

if response.status_code == 200 and response.json().get('success'):
    token = response.json().get('token')
    print('Token:', token)
    
    headers = {'Authorization': f'Bearer {token}'}
    
    list_url = f'{base_url}/system/conferenceRoom/list?pageNum=1&pageSize=10'
    list_response = requests.get(list_url, headers=headers)
    print('List response:', list_response.json())
    
    delete_url = f'{base_url}/system/conferenceRoom/13'
    
    delete_response = requests.delete(delete_url, headers=headers)
    print('Delete response:', delete_response.json())
    print('Delete status code:', delete_response.status_code)
    
    list_response2 = requests.get(list_url, headers=headers)
    print('List after delete:', list_response2.json())
else:
    print('Login failed')