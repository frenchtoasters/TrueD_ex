'''
Might need these later


from boa.interop.Neo.Runtime import CheckWitness
from boa.interop.Neo.Blockchain import GetHeight
from boa.interop.Neo.Action import RegisterAction
from MCTDex.common.Txio import Attachments, get_asset_attachments
'''
from boa.builtins import list
# Neo operations
from boa.interop.Neo.Runtime import CheckWitness, GetTime

from Constants import NeoAssetID, GasAssetID, OWNER, bucket_duration, system_asset
# Transaction actions
from Transactions import transfer_asset_to, reduce_balance
# Contract constants
from Constants import fee_factor, native_token, native_token_discount
# Exchange actions
from Exchange import get_state, get_maker_fee, get_taker_fee, get_volume, add_volume
# Storage manager
from MCTManager import get, put, delete, deserialize, serialize_array
# Notification actions ------ Might not be needed later
from Notifications import created, failed, transferred, filled, cancelled


def create_offer():
    '''
    Offer Object
    Category == Script Hash of the Asset
    '''
    offer = {
        "MakerAddress": '',
        "OfferAssetID": '',
        "OfferAssetCategory": '',
        "WantAssetID": '',
        "WantAssetCategory": '',
        "WantAmount": 0,
        "AvailableAmount": 0,
        "TradingPair": '',
        "Nonce": ''
    }
    return offer


def set_volume():
    volume = {
        "Native": 0,
        "Foreign": 0
    }
    return volume


def new_offer(maker_address, offer_asset_id, offer_amount, want_asset_id, want_amount, avail_amount, nonce):
    offer_asset_category = "NEP5"
    want_asset_category = "NEP5"

    if len(offer_asset_id) == 32:
        offer_asset_category = system_asset
    if len(want_asset_id) == 32:
        want_asset_category = system_asset

    offer = create_offer()

    offer["MakerAddress"] = maker_address
    offer["OfferAssetID"] = offer_asset_id
    offer["OfferAssetCategory"] = offer_asset_category
    offer["OfferAmount"] = offer_amount
    offer["WantAssetID"] = want_asset_id
    offer["WantAssetCategory"] = want_asset_category
    offer["WantAmount"] = want_amount
    offer["AvailableAmount"] = avail_amount
    offer["Nonce"] = nonce

    return offer


def get_offers(trading_pair) -> list:
    '''
    Get List of Offers for trading pair
    :param trading_pair: scripthash of each contract trading pair
    :return: list of Offers()
    '''
    result_serialized = get(trading_pair)

    if not result_serialized:
        print("result_serialized is null")
        return False

    result_info = deserialize(result_serialized)

    offers = []
    for result in result_info:
        offer = create_offer()
        offer["MakerAddress"] = result["MakerAddress"]
        offer["OfferAssetID"] = result["OfferAssetID"]
        offer["OfferAssetCategory"] = result["OfferAssetCategory"]
        offer["OfferAmount"] = result["OfferAmount"]
        offer["WantAssetID"] = result["WantAssetID"]
        offer["WantAssetCategory"] = result["WantAssetCategory"]
        offer["WantAmount"] = result["WantAmount"]
        offer["AvailableAmount"] = result["AvailableAmount"]
        offer["TradingPair"] = result["OfferAssetCategory"] + result["WantAssetCategory"]
        offers.append(offer)

    return offers


def get_offer(trading_pair, hash):
    '''
    Get Single Offer
    :param trading_pair:
    :param hash:
    :return: Offer Object
    '''
    offer_data = get(trading_pair + hash)

    if len(offer_data) == 0:
        return create_offer()
    else:
        return deserialize(offer_data)


def store_offer(trading_pair, offer_hash, offer):
    '''
    Store Single Offer
    :param trading_pair:
    :param offer_hash:
    :param offer:
    :return: Out put of Storage Call
    '''
    if offer["AvailableAmount"] == 0:
        remove_offer(trading_pair, offer_hash)
    else:
        offer_data = serialize_array(offer)
        put(trading_pair + offer_hash, offer_data)


def remove_offer(trading_pair, offer_hash):
    '''
    Remove Single Offer
    :param trading_pair:
    :param offer_hash:
    :return: Out put of Storage Call
    '''
    delete(trading_pair + offer_hash)


def make_offer(offer) -> bool:
    '''
    Make New Offer on books
    :param offer:
    :return: Result of if offer was valid
    '''
    if not CheckWitness(offer.MakerAddress):
        return False

    # Checking that the person that invoked this was the smart contract it self
    if not CheckWitness(OWNER):
        return False

    allowed = get_state()
    if allowed == 'Inactive' or allowed == 'Pending':
        return False

    if (
            allowed == 'Terminated' and not
            offer["OfferAssetID"] == NeoAssetID and offer["WantAssetID"] == GasAssetID and not
            offer["WantAssetID"] == NeoAssetID and offer["OfferAssetID"] == GasAssetID
    ):
        return False
    trading_pair = offer["OfferAssetID"] + offer["WantAssetID"]
    offer_hash = hash(offer)
    if get(trading_pair + offer_hash):
        return False

    if not offer["OfferAmount"] > 0 and offer["WantAmount"] > 0:
        return False

    if offer["OfferAssetID"] == offer["WantAssetID"]:
        return False

    if (
        len(offer["OfferAssetID"]) != 20 and len(offer["OfferAssetID"]) != 32 or
        len(offer["WantAssetID"]) != 20 and len(offer["WantAssetID"]) != 32
    ):
        return False

    if not reduce_balance(offer["MakerAddress"], offer["OfferAssetID"], offer["OfferAmount"]):
        return False

    store_offer(trading_pair, offer_hash, offer)

    created(offer["MakerAddress"], offer_hash, offer["OfferAssetID"], offer["OfferAmount"], offer["WantAssetID"], offer["WantAmount"])

    return True


def fill_offer(filler_address, trading_pair, offer_hash, amount_to_fill, use_native_token):
    if not CheckWitness(filler_address):
        return False

    # Checking that the person that invoked this was the smart contract
    if not CheckWitness(OWNER):
        return False

    offer = get_offer(trading_pair, offer_hash)

    if offer["MakerAddress"] == '':
        failed(filler_address, offer_hash)
        return False

    allowed = get_state()
    if allowed == 'Inactive' or allowed == 'Pending':
        return False

    if (
            allowed == 'Terminated' and not
            offer["OfferAssetID"] == NeoAssetID and offer["WantAssetID"] == GasAssetID and not
            offer["WantAssetID"] == NeoAssetID and offer["OfferAssetID"] == GasAssetID
    ):
        return False

    if filler_address == offer["MakerAddress"]:
        return False

    amount_to_take = (offer["OfferAmount"] * offer["WantAmount"]) / offer["OfferAmount"]
    if amount_to_take > offer["AvailableAmount"]:
        amount_to_take = offer["AvailableAmount"]
        amount_to_fill = (amount_to_take * offer["WantAmount"]) / offer["OfferAmount"]

    if amount_to_take <= 0:
        failed(filler_address, offer_hash)
        return True

    fee_address = get('feeAddress')
    maker_fee_rate = get_maker_fee(offer["WantAssetID"])
    taker_fee_rate = get_taker_fee(offer["OfferAssetID"])
    maker_fee = (amount_to_fill * maker_fee_rate) / fee_factor
    taker_fee = (amount_to_take * taker_fee_rate) / fee_factor
    native_fee = 0

    if use_native_token and offer["OfferAssetID"] != native_token:
        time = GetTime()
        bucket_number = time / bucket_duration
        volume = get_volume(bucket_number, offer["OfferAssetID"])

        native_volume = volume["Native"]
        foreign_volume = volume["Foreign"]

        if foreign_volume > 0:
            native_fee = (taker_fee * native_volume) / (foreign_volume * native_token_discount)

        if not reduce_balance(filler_address, native_token, native_fee):
            native_fee = 0

    if offer["OfferAssetID"] == native_token:
        taker_fee = taker_fee / native_token_discount

    if native_fee > 0:
        taker_amount = amount_to_take - taker_fee
    else:
        taker_amount = 0

    # Transfer to taker
    transfer_asset_to(filler_address, offer["WantAssetID"], taker_amount)
    transferred(filler_address, offer["OfferAssetID"], taker_amount)

    # Transfer to maker
    maker_amount = amount_to_fill - maker_fee
    transfer_asset_to(offer["MakerAddress"], offer["WantAssetID"], maker_amount)
    transferred(offer["MakerAddress"], offer["WantAssetID"], maker_amount)

    # Move fees
    if maker_fee > 0:
        transfer_asset_to(fee_address, offer["WantAssetID, maker_fee"])

    if native_fee == 0 and offer["OfferAssetID"] != native_token:
        transfer_asset_to(fee_address, offer["OfferAssetID"], taker_fee)

    # Update native token exchange rate
    if offer["OfferAssetID"] == native_token:
        add_volume(offer["WantAssetID"], amount_to_take, amount_to_fill)

    if offer["WantAssetID"] == native_token:
        add_volume(offer["OfferAssetID"], amount_to_fill, amount_to_take)

    # Update available amount
    offer["AvailableAmount"] = offer["AvailableAmount"] - amount_to_take

    store_offer(trading_pair, offer_hash, offer)

    filled(filler_address, offer_hash, amount_to_fill, offer["OfferAssetID"], offer["OfferAmount"], offer["WantAssetID"], offer["WantAmount"])

    return True


def cancel_offer(trading_pair, offer_hash):
    offer = get_offer(trading_pair, offer_hash)

    if offer.MakerAddress == '':
        return False

    if not CheckWitness(offer["MakerAddress"]):
        return False

    transfer_asset_to(offer["MakerAddress"], offer["OfferAssetID"], offer["AvailableAmount"])

    remove_offer(trading_pair, offer_hash)

    cancelled(offer["MakerAddress"], offer_hash)

    return True

