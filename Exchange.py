# Neo operations
from boa.builtins import concat

# Contract constants
from Constants import max_fee
# Storage Manager
from MCTManager import put, get


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

