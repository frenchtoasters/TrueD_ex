# Neo operations
from boa.interop.Neo.App import RegisterAppCall
from boa.builtins import concat, list, range, take, substr

# Contract constants
from actions.Constants import OWNER


'''
    Wrapper for the MCT Storage Calls
'''
ctx = RegisterAppCall('c186bcb4dc6db8e08be09191c6173456144c4b8d','operation','args')


def get(key):
    return ctx('Get', [key])


def delete(key):
    return ctx('Delete', [key])


def put(key, value):
    return ctx('Put', [key, value])


def transfer(my_hash, amount):
    return ctx('transfer', [my_hash, OWNER, amount])


def deserialize(data):

    collection_length_length = substr(data, 0, 1)

    collection_len = substr(data, 1, collection_length_length)

    new_collection = list(length=collection_len)

    offset = 1 + collection_length_length

    newdata = data[offset:]

    for i in range(0, collection_len):

        datalen_len = substr(newdata, 0, 1)

        data_len = substr(newdata, 1, datalen_len)

        start = 1 + datalen_len
        stop = start + data_len

        data = substr(newdata, start, data_len)

        new_collection[i] = data

        newdata = newdata[stop:]

    return new_collection


def serialize_array(items):
    item_length = serialize_length_item(items)

    output = item_length

    for item in items:
        itemlen = serialize_length_item(item)

        output = concat(output, itemlen)

        output = concat(output, item)

    return output


def serialize_length_item(item: list):
    thing_len = len(item)

    if thing_len <= 255:
        byte_len = b'\x02'
    else:
        byte_len = b'\x04'

    out = concat(byte_len, thing_len)

    return out
