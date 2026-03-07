import requests

# Login
lr = requests.post('http://localhost:8000/auth/login', 
    json={'email': 'admin@aegis-ids.local', 'senha': 'admin123'})
print(f'Login Status: {lr.status_code}')

if lr.status_code == 200:
    token = lr.json()['access_token']
    print('✓ Login successful')
    
    # Create user
    headers = {'Authorization': f'Bearer {token}'}
    user_data = {
        'nome': 'NewUser',
        'email': 'newuser@test.com',
        'senha': 'test123',
        'role': 'analista',
        'ativo': True
    }
    cr = requests.post('http://localhost:8000/auth/criar-usuario', 
        json=user_data, headers=headers)
    print(f'Create Status: {cr.status_code}')
    print(f'Response: {cr.json()}')
else:
    print(f'Login failed: {lr.text}')
