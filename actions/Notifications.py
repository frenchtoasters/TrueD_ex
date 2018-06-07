def created(MakerAddress, offer_hash, OfferAssetID, OfferAmount, WantAssetID, WantAmount):
    return True


def failed(filler_address, offer_hash):
    return True


def transferred(filler_address, OfferAssetID, taker_amount):
    return True


def filled(filler_address, offer_hash, amount_to_fill, OfferAssetID, OfferAmount, WantAssetID, WantAmount):
    return True


def cancelled(MakerAddress, offer_hash):
    return True
