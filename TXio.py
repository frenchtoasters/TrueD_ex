from boa.interop.System.ExecutionEngine import GetExecutingScriptHash, GetScriptContainer
from boa.interop.Neo.Transaction import Transaction, GetReferences, GetInputs, GetOutputs, GetUnspentCoins
from boa.interop.Neo.Blockchain import GetTransaction
from boa.interop.Neo.Output import GetValue, GetAssetId, GetScriptHash
from boa.interop.Neo.Input import GetInputHash, GetIndex


def attachments():
    """
    Container object ( struct ) for passing around information about attached neo and gas
    """
    attachment = {
        "neo_attached": 0,
        "gas_attached": 0,
        "neo_attached_received": 0,
        "gas_attached_received": 0,
        "sender_addr": 0,
        "receiver_addr": 0,
        "neo_asset_id": b'\x9b|\xff\xda\xa6t\xbe\xae\x0f\x93\x0e\xbe`\x85\xaf\x90\x93\xe5\xfeV\xb3J\\"\x0c\xcd\xcfn\xfc3o\xc5',
        "gas_asset_id": b'\xe7-(iy\xeel\xb1\xb7\xe6]\xfd\xdf\xb2\xe3\x84\x10\x0b\x8d\x14\x8ewX\xdeB\xe4\x16\x8bqy,`',
        "unspent_coins": 0
    }
    return attachment


def get_asset_attachments():
    """
    Gets information about NEO and Gas attached to an invocation TX
    :return:
        Attachments: An object with information about attached neo and gas
    """
    attachment = attachments()

    tx = GetScriptContainer()  # type:Transaction
    references = tx.References

    attachment["receiver_addr"] = GetExecutingScriptHash()

    if len(references) > 0:

        reference = references[0]
        attachment["sender_addr"] = reference.ScriptHash

        sent_amount_neo = 0
        sent_amount_gas = 0

        received_amount_neo = 0
        received_amount_gas = 0

        for output in tx.Outputs:
            if output.ScriptHash == attachment["receiver_addr"] and output.AssetId == attachment["neo_asset_id"]:
                sent_amount_neo += output.Value

            if output.ScriptHash == attachment["receiver_addr"] and output.AssetId == attachment["gas_asset_id"]:
                sent_amount_gas += output.Value

            if output.ScriptHash == attachment["sender_addr"] and output.AssetId == attachment["neo_asset_id"]:
                received_amount_neo += output.Value

            if output.ScriptHash == attachment["sender_addr"] and output.AssetId == attachment["gas_asset_id"]:
                received_amount_gas += output.Value

        attachment.neo_attached = sent_amount_neo
        attachment.gas_attached = sent_amount_gas

        attachment.neo_attached_received = received_amount_neo
        attachment.gas_attached_received = received_amount_gas

    return attachment


def get_asset_attachments_for_prev():
    attachment = attachments()

    tx = GetScriptContainer()  # type:Transaction

    sent_amount_neo = 0
    sent_amount_gas = 0

    attachment.receiver_addr = GetExecutingScriptHash()

    for ins in tx.Inputs:

        prev_tx = GetTransaction(ins.Hash)
        references = prev_tx.References

        if len(references) > 0:

            reference = references[0]
            sender_addr = reference.ScriptHash

            prev_output = prev_tx.Outputs[ins.Index]

            if prev_output.ScriptHash == attachment["receiver_addr"] and prev_output.AssetId == attachment["neo_asset_id"]:
                sent_amount_neo += prev_output.Value

            if prev_output.ScriptHash == attachment["receiver_addr"] and prev_output.AssetId == attachment["gas_asset_id"]:
                sent_amount_gas += prev_output.Value

    attachment.neo_attached = sent_amount_neo
    attachment.gas_attached = sent_amount_gas

    return attachment


def validate_inputs(tx):
    return True

