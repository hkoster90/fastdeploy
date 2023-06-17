import pytest
from inventory import InventoryManager, DuplicateHostnameError, Host, HostGroup, Variable
import pymongo

MONGO_CONNECTION_STRING = "mongodb://10.232.16.250:27017/"
MONGO_DATABASE_NAME = "inventory_db_test"
MONGO_COLLECTION = "hosts_collection"


@pytest.fixture
def mongo_collection():
    # Create a connection to the local MongoDB instance
    client = pymongo.MongoClient("mongodb://10.232.16.250:27017/")
    db = client['inventory_db_test']
    collection = db['hosts_collection']

    # Clean up existing data before each test
    collection.delete_many({})

    return collection

# Tests that a single host can be added to the inventory
def test_add_single_host(mongo_collection):
    # Arrange
    manager = InventoryManager(MONGO_CONNECTION_STRING, MONGO_DATABASE_NAME, MONGO_COLLECTION)
    host = Host(hostname='test_host', ip_address='192.168.1.1',
                password='password', private_key_path='path/to/key')

    # Act
    manager.add_host(host)
    result = manager.get_host_by_name('test_host')

    # Assert
    assert result is not None
    assert result.hostname == 'test_host'
    assert result.ip_address == '192.168.1.1'
    assert result.password != 'password'
    assert result.private_key_path == 'path/to/key'

# Tests that multiple hosts can be added to the inventory
def test_add_multiple_hosts(mongo_collection):
    # Arrange
    manager = InventoryManager(MONGO_CONNECTION_STRING, MONGO_DATABASE_NAME, MONGO_COLLECTION)
    hosts = [
        Host(hostname='test_host1', ip_address='192.168.1.1',
                password='password1', private_key_path='path/to/key1'),
        Host(hostname='test_host2', ip_address='192.168.1.2',
                password='password2', private_key_path='path/to/key2'),
        Host(hostname='test_host3', ip_address='192.168.1.3',
                password='password3', private_key_path='path/to/key3')
    ]

    # Act
    manager.add_hosts(hosts)
    result1 = manager.get_host_by_name('test_host1')
    result2 = manager.get_host_by_name('test_host2')
    result3 = manager.get_host_by_name('test_host3')

    # Assert
    assert result1 is not None
    assert result1.hostname == 'test_host1'
    assert result1.ip_address == '192.168.1.1'
    assert result1.password != 'password1'
    assert result1.private_key_path == 'path/to/key1'

    assert result2 is not None
    assert result2.hostname == 'test_host2'
    assert result2.ip_address == '192.168.1.2'
    assert result2.password != 'password2'
    assert result2.private_key_path == 'path/to/key2'

    assert result3 is not None
    assert result3.hostname == 'test_host3'
    assert result3.ip_address == '192.168.1.3'
    assert result3.password != 'password3'
    assert result3.private_key_path == 'path/to/key3'

# Tests that a host can be updated in the inventory
def test_update_host(mongo_collection):
    # Arrange
    manager = InventoryManager(MONGO_CONNECTION_STRING, MONGO_DATABASE_NAME, MONGO_COLLECTION)
    host = Host(hostname='test_host', ip_address='192.168.1.1',
                password='password', private_key_path='path/to/key')
    manager.add_host(host)

    # Act
    manager.update_host('test_host', {'ip_address': '192.168.1.2'})
    result = manager.get_host_by_name('test_host')

    # Assert
    assert result is not None
    assert result.hostname == 'test_host'
    assert result.ip_address == '192.168.1.2'
    assert result.password != 'password'
    assert result.private_key_path == 'path/to/key'

# Tests that a host can be deleted from the inventory
def test_delete_host(mongo_collection):
    # Arrange
    manager = InventoryManager(MONGO_CONNECTION_STRING, MONGO_DATABASE_NAME, MONGO_COLLECTION)
    host = Host(hostname='test_host', ip_address='192.168.1.1',
                password='password', private_key_path='path/to/key')
    manager.add_host(host)

    # Act
    manager.delete_host('test_host')
    result = manager.get_host_by_name('test_host')

    # Assert
    assert result is None

# Tests that a host can be retrieved by its name
def test_get_host_by_name(mongo_collection):
    # Arrange
    manager = InventoryManager(MONGO_CONNECTION_STRING, MONGO_DATABASE_NAME, MONGO_COLLECTION)
    host = Host(hostname='test_host', ip_address='192.168.1.1',
                password='password', private_key_path='path/to/key')
    manager.add_host(host)

    # Act
    result = manager.get_host_by_name('test_host')

    # Assert
    assert result is not None
    assert result.hostname == 'test_host'
    assert result.ip_address == '192.168.1.1'
    assert result.password != 'password'
    assert result.private_key_path == 'path/to/key'

# Tests that all hosts can be retrieved from the inventory
def test_get_all_hosts(mongo_collection):
    # Arrange
    manager = InventoryManager(MONGO_CONNECTION_STRING, MONGO_DATABASE_NAME, MONGO_COLLECTION)
    hosts = [
        Host(hostname='test_host1', ip_address='192.168.1.1',
                password='password1', private_key_path='path/to/key1'),
        Host(hostname='test_host2', ip_address='192.168.1.2',
                password='password2', private_key_path='path/to/key2'),
        Host(hostname='test_host3', ip_address='192.168.1.3',
                password='password3', private_key_path='path/to/key3')
        ]
    manager.add_hosts(hosts)

    # Act
    result = manager.get_hosts()

    # Assert
    assert len(result) == 3
    assert result[0].hostname == 'test_host1'
    assert result[0].ip_address == '192.168.1.1'
    assert result[0].password != 'password1'
    assert result[0].private_key_path == 'path/to/key1'

    assert result[1].hostname == 'test_host2'
    assert result[1].ip_address == '192.168.1.2'
    assert result[1].password != 'password2'
    assert result[1].private_key_path == 'path/to/key2'

    assert result[2].hostname == 'test_host3'
    assert result[2].ip_address == '192.168.1.3'
    assert result[2].password != 'password3'
    assert result[2].private_key_path == 'path/to/key3'

# Tests that all hosts can be retrieved from the inventory
def test_get_all_hosts(mongo_collection):
    # Arrange
    manager = InventoryManager(MONGO_CONNECTION_STRING, MONGO_DATABASE_NAME, MONGO_COLLECTION)
    hosts = [
        Host(hostname='test_host1', ip_address='192.168.1.1',
            password='password1', private_key_path='path/to/key1'),
        Host(hostname='test_host2', ip_address='192.168.1.2',
            password='password2', private_key_path='path/to/key2'),
        Host(hostname='test_host3', ip_address='192.168.1.3',
            password='password3', private_key_path='path/to/key3')
    ]
    manager.add_hosts(hosts)

    # Act
    result = manager.get_hosts()

    # Assert
    assert len(result) == 3
    assert result[0].hostname == 'test_host1'
    assert result[0].ip_address == '192.168.1.1'
    assert result[0].password != 'password1'
    assert result[0].private_key_path == 'path/to/key1'

    assert result[1].hostname == 'test_host2'
    assert result[1].ip_address == '192.168.1.2'
    assert result[1].password != 'password2'
    assert result[1].private_key_path == 'path/to/key2'

    assert result[2].hostname == 'test_host3'
    assert result[2].ip_address == '192.168.1.3'
    assert result[2].password != 'password3'
    assert result[2].private_key_path == 'path/to/key3'
