# Neo operations
from boa.interop.Neo.Runtime import Notify
from boa.interop.System.ExecutionEngine import GetExecutingScriptHash, GetCallingScriptHash, GetScriptContainer
from boa.builtins import concat

# Storage manager
from common.MCTManager import MCTManager


def transfer_asset_to(address, asset_id, amount):

    storage = MCTManager()

    if amount < 1:
        Notify("Amount to transfer less than 1!")
        return

    key = concat(address, asset_id)
    current_balance = storage.get(key)
    storage.put(key, current_balance + amount)


def reduce_balance(address, asset_id, amount):

    storage = MCTManager()

    if amount < 1:
        Notify("Amount to reduce less than 1")
        return False

    key = concat(address, asset_id)
    current_balance = storage.get(key)
    new_balance = current_balance - amount

    if new_balance < 0:
        Notify("Not enough balance")
        return False

    if new_balance > 0:
        storage.put(key, new_balance)
    else:
        storage.delete(key)

    return True


def verify_sent_amount(address, asset_id, amount):
    return True


def process_withdrawal():
    my_container = GetScriptContainer()
    my_hash = GetExecutingScriptHash()
    withdrawl_stage = WithdrawStage(my_container)
    if withdrawl_stage is None:
        return False

    withdrawingaddr = getWithdrawAddress(mycontainer, withdrawlstage)
    assetID = getWithdrawlAsset(mycontainer)
    if len(assetID) == 20:
        iswithdrawingNEP5 = True
    else:
        iswithdrawingNEP5 = False

    # inputs = mycontainer.getInputs()
    # outputs = mycontainer.getOutputs()

    if withdrawlstage == 'Mark':
        amount = getbalance(withdrawingaddr, assetID)
        # Here you can add withdraw fees and things like that
        markwithdrawal(withdrawingaddr, assetID, amount)

    byteArray = ['0']
    if iswithdrawingNEP5:
        put(myhash + byteArray, withdrawingaddr)
    # else:
    #   value = 0
    #   for output in outputs:
    #       value += outputs[output]['Value']

    withdrawing(withdrawingaddr, assetID, amount)
    return True
