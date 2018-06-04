# Neo operations
from boa.interop.Neo.Runtime import GetTime
from boa.builtins import concat

# Contract constants
from actions.Constants import bucket_duration, max_fee

# Storage Manager
from common.MCTManager import MCTManager

# Offer actions
from common.Offer import Volume


# Owner functions
def freeze_trading():
    storage = MCTManager()

    storage.put("state", "Inactive")


def unfreeze_trading():
    storage = MCTManager()

    storage.put("state", "Active")


def terminate_trading():
    storage = MCTManager()

    storage.put("state", "terminated")


def set_maker_fee(fee, asset_id):
    if fee > max_fee:
        return False
    if fee < 0:
        return False

    storage = MCTManager()

    key = concat("makerFee", asset_id)
    storage.put(key, fee)


def set_taker_fee(fee, asset_id):
    if fee > max_fee:
        return False
    if fee < 0:
        return False

    storage = MCTManager()

    key = concat("takerFee", asset_id)
    storage.put(key, fee)


def set_fee_address(fee_address):
    if len(fee_address) != 20:
        return False

    storage = MCTManager()

    storage.put("feeAddress", fee_address)


def add_to_whitelist():
    return True


def remove_from_whitelist():
    return True


def destory_whitelist():
    return True


def initialize():
    storage = MCTManager()
    storage.put('state', 'Active')


# Utility functions
def get_state():
    storage = MCTManager()
    return storage.get('state')


def get_maker_fee(asset_id):
    storage = MCTManager()

    key = concat("makerFee", asset_id)
    fee = storage.get(key)

    if len(fee) != 0 or len(asset_id) == 0:
        return fee

    return storage.get("makerFee")


def get_taker_fee(asset_id):
    storage = MCTManager()

    key = concat("takerFee", asset_id)
    fee = storage.get(key)

    if len(fee) != 0 or len(asset_id) == 0:
        return fee

    return storage.get("takerFee")


def get_balance(originator, asset_id):
    storage = MCTManager()
    key = concat(originator, asset_id)
    return storage.get(key)


def get_exchange_rate(asset_id):
    time = GetTime()

    bucket_number = time / bucket_duration

    return get_volume(bucket_number, asset_id)


def get_volume(bucket_number, asset_id):
    storage = MCTManager()

    volume_key = concat("tradeVolume", bucket_number)
    volume_key = concat(volume_key, asset_id)
    volume_data = storage.get(volume_key)

    if len(volume_data) == 0:
        return Volume()
    else:
        return storage.deserialize(volume_data)


def add_volume(asset_id, native_amount, foreign_amount):
    time = GetTime()
    storage = MCTManager()

    bucket_number = time / bucket_duration

    volume_key = concat("tradeVolume", bucket_number)
    volume_key = concat(volume_key, asset_id)

    volume_data = storage.get(volume_key)

    if len(volume_data) == 0:
        volume = Volume()

        volume.Native = native_amount
        volume.Foreign = foreign_amount
    else:
        volume = storage.deserialize(volume_data)
        volume.Native = volume.Native + native_amount
        volume.Foreign = volume.Foreign + foreign_amount

    storage.put(volume_key, storage.serialize_array(volume))

