from flaskr import create_app
from logging import getLogger

logger = getLogger(__name__)

    
def test_home(client):
    response = client.get('/')
    logger.warning(response.data)
    assert b'samrah' in response.data
    