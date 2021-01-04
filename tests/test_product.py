import pytest
from flaskr.db import get_db



def test_index(client):
    response = client.get('/product/')
    assert b'apple' in response.data
    assert b'QTY: 100' in response.data
    assert b'href="/product/1/update"' in response.data
    assert b'href="/product/1/delete"' in response.data
    
    
def test_create(client, app):
   
    assert client.get('/product/create').status_code == 200
    client.post('/product/create', data={'title': 'banana', 'qty': 100 , 'image': 'default_image.jpg'})

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(product_id) FROM product').fetchone()[0]
        assert count == 3


def test_update(client, app):
    assert client.get('/product/1/update').status_code == 200
    client.post('/product/1/update', data={'title': 'eggs', 'qty': 100 , 'image': 'default_image.jpg'})

    with app.app_context():
        db = get_db()
        product = db.execute('SELECT * FROM product WHERE product_id = 1').fetchone()
        assert product['title'] == 'eggs'


@pytest.mark.parametrize('path', (
    '/product/create',
    '/product/1/update',
))
def test_create_update_validate(client, path):
    response = client.post(path,data={'title': '', 'qty': 100 , 'image': 'default_image.jpg'})
    assert b'Title is required.' in response.data
    
    
def test_delete(client, app):
    response = client.post('/product/1/delete')
    assert response.headers['Location'] == 'http://localhost:5000/product/'

    with app.app_context():
        db = get_db()
        product = db.execute('SELECT * FROM product WHERE product_id = 1').fetchone()
        assert product is None