import pytest
from flaskr.db import get_db
from io import BytesIO


def test_index(client):
    response = client.get('/location/') 
    assert b'Nablus' in response.data
    assert b'Added In 2021-01-04' in response.data
    assert b'href="/location/1/update"' in response.data
    assert b'href="/location/1/delete"' in response.data
    
    
def test_create(client, app):
   
    assert client.get('/location/create').status_code == 200
    image = "../flaskr/static/images/location_default.jpg"
    
    data = {'name': 'ldldld'}
    with open(image, 'rb') as f: 
        data['file'] = (f, f.name)
    client.post('/location/create',content_type='multipart/form-data' ,data=data)

    with app.app_context():
        db = get_db()
        BytesIO(b'my file contents'), "work_order.123"
        count = db.execute('SELECT COUNT(location_id) FROM location').fetchone()[0]
        assert count == 3


def test_update(client, app):
    assert client.get('/location/1/update').status_code == 200
    client.post('/location/1/update', data={'name': 'Qalqeliah','image': 'location_default.jpg'})

    with app.app_context():
        db = get_db()
        location = db.execute('SELECT * FROM location WHERE location_id = 1').fetchone()
        assert location['name'] == 'Qalqeliah'



    
def test_delete(client, app):
    response = client.post('/location/1/delete')
    assert response.headers['Location'] == 'http://localhost:5000/location/'

    with app.app_context():
        db = get_db()
        location = db.execute('SELECT * FROM location WHERE location_id = 1').fetchone()
        assert location is None