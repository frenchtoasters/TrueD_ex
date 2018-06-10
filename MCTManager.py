'''
Name: MCTManager.py
Author: Tyler French
Description: Class used for all MCT storage operations, as well as additional storage operations.
Example:
    from MCTManager import get, put, delete, transfer, deserialize, serialize_array

    get(key)
    put(key, value)
    delete(key)
    transfer(tx_hash, amount)
    serialize_array(array)
'''

# Neo operations
from boa.interop.Neo.App import RegisterAppCall
from boa.interop.Neo.Runtime import Serialize, Deserialize

# Contract constants
from Constants import OWNER

'''
    Wrapper for the MCT Storage Calls
'''
ctx = RegisterAppCall('c186bcb4dc6db8e08be09191c6173456144c4b8d', 'operation', 'args')


def get(key):
    return ctx('Get', [key])


def delete(key):
    return ctx('Delete', [key])


def put(key, value):
    return ctx('Put', [key, value])


def transfer(my_hash, amount):
    return ctx('transfer', [my_hash, OWNER, amount])


def deserialize(data):
    '''
    This function deserialize's an offer from storage
    :param data:
    :return: data
    '''
    return Deserialize(data)


def serialize_array(items):
    '''
    This function serialize's and array of offers to be put in storage
    :param items:
    :return: data: hash of array of offers
    '''
    return Serialize(items)

