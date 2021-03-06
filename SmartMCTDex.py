# NEO operations
# Contract constants
from Constants import OWNER
from Exchange import freeze_trading, unfreeze_trading, terminate_trading, add_to_whitelist, \
    remove_from_whitelist, initialize, get_balance, get_maker_fee, get_taker_fee
# Storage Manager
from MCTManager import transfer, get
# Offer actions
from Offer import get_offers, new_offer, make_offer, fill_offer, cancel_offer, get_exchange_rate
from TXio import get_asset_attachments, get_asset_attachments_for_prev
# Transaction actions
from Transactions import transfer_asset_to, verify_sent_amount, process_withdrawal
from boa.interop.Neo.Runtime import GetTrigger, CheckWitness
from boa.interop.Neo.TriggerType import Application, Verification
from boa.interop.System.ExecutionEngine import GetExecutingScriptHash, GetScriptContainer
from boa.interop.Neo.Transaction import GetInputs, GetOutputs


def main(operation, args):
    trigger = GetTrigger()

    if trigger == Verification():
        '''
        Validate inputs
        Check that valid self send
        Validate is withdrawing nep5
        Validate utxo has been reserved
        Validate withdraw destination
        Validate amount withdrawn
        '''
        if get("state") != 'Active':
            return False

        tx_data = get_asset_attachments()
        prev_tx_data = get_asset_attachments_for_prev()

        # THIS WILL NEED TO BE CALLING A FUNCTION LATER
        withdrawal_stage = 'Mark'

        if withdrawal_stage == 'Mark':
            if not CheckWitness(tx_data["sender_addr"]):
                return False
            '''
            if not verify_withdrawal(tx_data):
                return False
                    // Validate inputs as well
                    foreach (var i in inputs)
                    {
                        if (Storage.Get(Context(), i.PrevHash.Concat(IndexAsByteArray(i.PrevIndex))).Length > 0) return false;
                    }
            '''
        tx = GetScriptContainer()
        inputs = GetInputs(tx)
        outputs = GetOutputs(tx)

        if CheckWitness(OWNER):
            return True
        return False

    elif trigger == Application():

        if operation == 'initialize':
            if not CheckWitness(OWNER):
                print("initialize error")
                return False
            if len(args) != 3:
                print("To few args")
                return False
            return initialize()

        # Get functions
        if operation == 'getstate':
            return get("state")

        # ARGS: asset_id
        if operation == 'getMakerFee':
            return get_maker_fee(args[0])

        # ARGS: asset_id
        if operation == 'getTakerFee':
            return get_taker_fee(args[0])

        # ARGS: asset_id
        if operation == 'getExchangeRate':
            return get_exchange_rate(args[0])

        # ARGS: trading_pair
        if operation == 'getOffers':
            return get_offers(args[0])

        # ARGS: originator, asset_id
        if operation == 'getBalance':
            return get_balance(args[0], args[1])

        # Execute functions

        # ARGS: address, asset_id, amount
        if operation == 'deposit':
            if get("state") != 'Active':
                return False
            if len(args) != 3:
                return False
            if not verify_sent_amount(args[0], args[1], args[2]):
                return False
            if not transfer_asset_to(args[0], args[1], args[2]):
                return False
            return True

        # ARGS: maker_address, offer_asset_id, offer_amount, want_asset_id, want_amount, avail_amount, nonce
        if operation == 'makeOffer':
            if get("state") != 'Active':
                return False
            if len(args) != 7:
                return False

            offer = new_offer(args[0], args[1], args[2], args[3], args[4], args[5], args[6])
            return make_offer(offer)

        # ARGS: filler_address, trading_pair, offer_hash, amount_to_fill, use_native_token)
        if operation == 'fillOffer':
            if get("state") != 'Active':
                return False
            if len(args) != 5:
                return False

            return fill_offer(args[0], args[1], args[2], args[3], args[4])

        # ARGS: trading_pair, offer_hash
        if operation == 'cancelOffer':
            if get("state") != 'Active':
                return False

            if len(args) != 2:
                return False

            return cancel_offer(args[0], args[1])

        if operation == 'withdraw':
            return process_withdrawal()

        # Owner Operations
        if not CheckWitness(OWNER):
            return False

        if operation == 'freezeTrading':
            return freeze_trading()

        if operation == 'unfreezeTrading':
            return unfreeze_trading()

        if operation == 'terminateTrading':
            return terminate_trading()

        if operation == 'addToWhitelist':
            return add_to_whitelist()

        if operation == 'removeFromWhitelist':
            return remove_from_whitelist()

        # ARGS: amount
        if operation == 'ownerWithdraw':
            if not CheckWitness(OWNER):
                print('Only the contract owner can withdraw MCT from the contract')
                return False

            if len(args) != 1:
                print('withdraw amount not specified')
                return False

            t_amount = args[0]
            my_hash = GetExecutingScriptHash()

            return transfer(my_hash, t_amount)

    return False
