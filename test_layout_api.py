import requests

base_url = 'http://localhost:9099/dev-api'

login_url = f'{base_url}/login'
login_data = {
    'username': 'admin',
    'password': 'admin123',
    'code': '',
    'uuid': ''
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
    
    room_id = 3
    layout_url = f'{base_url}/system/conferenceRoom/layout/room/{room_id}'
    layout_response = requests.get(layout_url, headers=headers)
    print('Get layout response:', layout_response.json())
    
    save_layout_url = f'{base_url}/system/conferenceRoom/layout/save'
    layout_data = {
        'roomId': room_id,
        'config': {
            'podiumStyle': 'bar',
            'rows': 5,
            'columns': 8,
            'seatNumberType': 'odd-even',
            'aisleCount': 1,
            'aisles': [{'aisleNumber': 1, 'direction': 'vertical', 'position': 4}],
            'showThumbnail': False
        },
        'seats': [
            [{'seat_number': 7, 'available': True}, {'seat_number': 5, 'available': True}, {'seat_number': 3, 'available': True}, {'seat_number': 1, 'available': True}, {'seat_number': 2, 'available': True}, {'seat_number': 4, 'available': True}, {'seat_number': 6, 'available': True}, {'seat_number': 8, 'available': True}],
            [{'seat_number': 7, 'available': True}, {'seat_number': 5, 'available': True}, {'seat_number': 3, 'available': True}, {'seat_number': 1, 'available': True}, {'seat_number': 2, 'available': True}, {'seat_number': 4, 'available': True}, {'seat_number': 6, 'available': True}, {'seat_number': 8, 'available': True}],
            [{'seat_number': 7, 'available': True}, {'seat_number': 5, 'available': True}, {'seat_number': 3, 'available': True}, {'seat_number': 1, 'available': True}, {'seat_number': 2, 'available': True}, {'seat_number': 4, 'available': True}, {'seat_number': 6, 'available': True}, {'seat_number': 8, 'available': True}],
            [{'seat_number': 7, 'available': True}, {'seat_number': 5, 'available': True}, {'seat_number': 3, 'available': True}, {'seat_number': 1, 'available': True}, {'seat_number': 2, 'available': True}, {'seat_number': 4, 'available': True}, {'seat_number': 6, 'available': True}, {'seat_number': 8, 'available': True}],
            [{'seat_number': 7, 'available': True}, {'seat_number': 5, 'available': True}, {'seat_number': 3, 'available': True}, {'seat_number': 1, 'available': True}, {'seat_number': 2, 'available': True}, {'seat_number': 4, 'available': True}, {'seat_number': 6, 'available': True}, {'seat_number': 8, 'available': True}]
        ]
    }
    save_response = requests.post(save_layout_url, json=layout_data, headers=headers)
    print('Save layout response:', save_response.json())
    
    layout_response2 = requests.get(layout_url, headers=headers)
    print('Get layout after save:', layout_response2.json())
else:
    print('Login failed')