# Neo operations
from boa.interop.Neo.Runtime import GetTime
from boa.builtins import concat

# Contract constants
from actions.Constants import bucket_duration, max_fee

# Storage Manager
from common.MCTManager import put, get, deserialize, serialize_array

# Offer actions
from common.Offer import set_volume


# Owner functions
def freeze_trading():
    put("state", "Inactive")


def unfreeze_trading():
    put("state", "Active")


def terminate_trading():
    put("state", "terminated")


def set_maker_fee(fee, asset_id):
    if fee > max_fee:
        return False
    if fee < 0:
        return False

    key = concat("makerFee", asset_id)
    put(key, fee)


def set_taker_fee(fee, asset_id):
    if fee > max_fee:
        return False
    if fee < 0:
        return False

    key = concat("takerFee", asset_id)
    put(key, fee)


def set_fee_address(fee_address):
    if len(fee_address) != 20:
        return False

    put("feeAddress", fee_address)


def add_to_whitelist():
    return True


def remove_from_whitelist():
    return True


def destory_whitelist():
    return True


def initialize():
    put('state', 'Active')


# Utility functions
def get_state():
    return get('state')


def get_maker_fee(asset_id):
    key = concat("makerFee", asset_id)
    fee = get(key)

    if len(fee) != 0 or len(asset_id) == 0:
        return fee

    return get("makerFee")


def get_taker_fee(asset_id):
    key = concat("takerFee", asset_id)
    fee = get(key)

    if len(fee) != 0 or len(asset_id) == 0:
        return fee

    return get("takerFee")


def get_balance(originator, asset_id):
    key = concat(originator, asset_id)
    return get(key)


def get_exchange_rate(asset_id):
    time = GetTime()

    bucket_number = time / bucket_duration

    return get_volume(bucket_number, asset_id)


def get_volume(bucket_number, asset_id):
    volume_key = concat("tradeVolume", bucket_number)
    volume_key = concat(volume_key, asset_id)
    volume_data = get(volume_key)

    if len(volume_data) == 0:
        return set_volume()
    else:
        return deserialize(volume_data)


def add_volume(asset_id, native_amount, foreign_amount):
    time = GetTime()

    bucket_number = time / bucket_duration

    volume_key = concat("tradeVolume", bucket_number)
    volume_key = concat(volume_key, asset_id)

    volume_data = get(volume_key)

    if len(volume_data) == 0:
        volume = set_volume()

        volume["Native"] = native_amount
        volume["Foreign"] = foreign_amount
    else:
        volume = deserialize(volume_data)
        volume["Native"] = volume["Native"] + native_amount
        volume["Foreign"] = volume["Foreign"] + foreign_amount

    put(volume_key, serialize_array(volume))
