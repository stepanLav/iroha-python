#!/usr/bin/env python3
#
# Copyright Soramitsu Co., Ltd. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#

import os
import binascii
from iroha import IrohaCrypto
from iroha import Iroha, IrohaGrpc
from iroha.primitive_pb2 import can_set_my_account_detail
import sys

if sys.version_info[0] < 3:
    raise Exception('Python 3 or a more recent version is required.')


IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', 'localhost')
IROHA_PORT = os.getenv('IROHA_PORT', '50051')
ADMIN_ACCOUNT_ID = 'root@root'
ADMIN_PRIVATE_KEY = '7a1cb487ed17a60efbf4aa21df74bb391fcc2260f87c83eb7de9c120d2112ec7'
iroha = Iroha(ADMIN_ACCOUNT_ID)
net = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR, IROHA_PORT))

'''
contract QueryIroha {
    address public serviceContractAddress;
    
    //Initializing service contract address in constructor
    constructor() public {
        serviceContractAddress = 0xA6Abc17819738299B3B2c1CE46d55c74f04E290C;
    }
    
    //Queries the balance in _asset of an Iroha _account
    function queryBalance(string memory _account, string memory _asset) public 
                    returns (bytes memory result) {
        bytes memory payload = abi.encodeWithSignature(
            "getAssetBalance(string,string)",
            _account,
            _asset);
        (bool success, bytes memory ret) = 
            address(serviceContractAddress).delegatecall(payload);
        require(success, "Error calling service contract function");
        result = ret;
    }
}
'''

'''
contract Transfer {
    address public serviceContractAddress;
    
    event Transferred(string indexed source, string indexed destination, string amount);
    
    //Initializing service contract address in constructor
    constructor() public {
        serviceContractAddress = 0xA6Abc17819738299B3B2c1CE46d55c74f04E290C;
    }
    
    //Queries the balance in _asset of an Iroha _account
    function transferAsset(string memory src, string memory dst,
                            string memory asset, string memory amount) public
                            returns (bytes memory result) {
        bytes memory payload = abi.encodeWithSignature(
            "transferAsset(string,string,string,string)",
            src,
            dst,
            asset,
            amount);
        (bool success, bytes memory ret) =
            address(serviceContractAddress).delegatecall(payload);
        require(success, "Error calling service contract function");
        
        emit Transferred(src, dst, amount);
        result = ret;
    }
    
}
'''

'''
contract Coin {
    // The keyword "public" makes variables
    // accessible from other contracts
    address public minter;
    mapping (address => uint) public balances;

    // Events allow clients to react to specific
    // contract changes you declare
    event Sent(address from, address to, uint amount);

    // Constructor code is only run when the contract
    // is created
    constructor() public {
        minter = msg.sender;
    }

    // Sends an amount of newly created coins to an address
    // Can only be called by the contract creator
    function mint(address receiver, uint amount) public {
        require(msg.sender == minter);
        require(amount < 1e60);
        balances[receiver] += amount;
    }

    // Sends an amount of existing coins
    // from any caller to an address
    function send(address receiver, uint amount) public {
        require(amount <= balances[msg.sender], "Insufficient balance.");
        balances[msg.sender] -= amount;
        balances[receiver] += amount;
        emit Sent(msg.sender, receiver, amount);
    }
}
'''
query_contract = '608060405234801561001057600080fd5b5073a6abc17819738299b3b2c1ce46d55c74f04e290c6000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff160217905550610573806100746000396000f3fe608060405234801561001057600080fd5b50600436106100365760003560e01c80632c74aaaf1461003b578063d4e804ab14610206575b600080fd5b61018b6004803603604081101561005157600080fd5b810190808035906020019064010000000081111561006e57600080fd5b82018360208201111561008057600080fd5b803590602001918460018302840111640100000000831117156100a257600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f8201169050808301925050505050505091929192908035906020019064010000000081111561010557600080fd5b82018360208201111561011757600080fd5b8035906020019184600183028401116401000000008311171561013957600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f820116905080830192505050505050509192919290505050610250565b6040518080602001828103825283818151815260200191508051906020019080838360005b838110156101cb5780820151818401526020810190506101b0565b50505050905090810190601f1680156101f85780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b61020e6104f1565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b6060808383604051602401808060200180602001838103835285818151815260200191508051906020019080838360005b8381101561029c578082015181840152602081019050610281565b50505050905090810190601f1680156102c95780820380516001836020036101000a031916815260200191505b50838103825284818151815260200191508051906020019080838360005b838110156103025780820151818401526020810190506102e7565b50505050905090810190601f16801561032f5780820380516001836020036101000a031916815260200191505b509450505050506040516020818303038152906040527f260b5d52000000000000000000000000000000000000000000000000000000007bffffffffffffffffffffffffffffffffffffffffffffffffffffffff19166020820180517bffffffffffffffffffffffffffffffffffffffffffffffffffffffff83818316178352505050509050600060606000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16836040518082805190602001908083835b602083106104255780518252602082019150602081019050602083039250610402565b6001836020036101000a038019825116818451168082178552505050505050905001915050600060405180830381855af49150503d8060008114610485576040519150601f19603f3d011682016040523d82523d6000602084013e61048a565b606091505b5091509150816104e5576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260278152602001806105176027913960400191505060405180910390fd5b80935050505092915050565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff168156fe4572726f722063616c6c696e67207365727669636520636f6e74726163742066756e6374696f6ea2646970667358221220b448b650a555a33ebb9be34d1af6218b21cb68964b99adb64d889303f168494364736f6c63430006060033'
transfer_contract = '608060405234801561001057600080fd5b5073a6abc17819738299b3b2c1ce46d55c74f04e290c6000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff1602179055506108db806100746000396000f3fe608060405234801561001057600080fd5b50600436106100365760003560e01c80632cddc4111461003b578063d4e804ab14610334575b600080fd5b6102b96004803603608081101561005157600080fd5b810190808035906020019064010000000081111561006e57600080fd5b82018360208201111561008057600080fd5b803590602001918460018302840111640100000000831117156100a257600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f8201169050808301925050505050505091929192908035906020019064010000000081111561010557600080fd5b82018360208201111561011757600080fd5b8035906020019184600183028401116401000000008311171561013957600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f8201169050808301925050505050505091929192908035906020019064010000000081111561019c57600080fd5b8201836020820111156101ae57600080fd5b803590602001918460018302840111640100000000831117156101d057600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f8201169050808301925050505050505091929192908035906020019064010000000081111561023357600080fd5b82018360208201111561024557600080fd5b8035906020019184600183028401116401000000008311171561026757600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f82011690508083019250505050505050919291929050505061037e565b6040518080602001828103825283818151815260200191508051906020019080838360005b838110156102f95780820151818401526020810190506102de565b50505050905090810190601f1680156103265780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b61033c610859565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b606080858585856040516024018080602001806020018060200180602001858103855289818151815260200191508051906020019080838360005b838110156103d45780820151818401526020810190506103b9565b50505050905090810190601f1680156104015780820380516001836020036101000a031916815260200191505b50858103845288818151815260200191508051906020019080838360005b8381101561043a57808201518184015260208101905061041f565b50505050905090810190601f1680156104675780820380516001836020036101000a031916815260200191505b50858103835287818151815260200191508051906020019080838360005b838110156104a0578082015181840152602081019050610485565b50505050905090810190601f1680156104cd5780820380516001836020036101000a031916815260200191505b50858103825286818151815260200191508051906020019080838360005b838110156105065780820151818401526020810190506104eb565b50505050905090810190601f1680156105335780820380516001836020036101000a031916815260200191505b50985050505050505050506040516020818303038152906040527f2cddc411000000000000000000000000000000000000000000000000000000007bffffffffffffffffffffffffffffffffffffffffffffffffffffffff19166020820180517bffffffffffffffffffffffffffffffffffffffffffffffffffffffff83818316178352505050509050600060606000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16836040518082805190602001908083835b6020831061062d578051825260208201915060208101905060208303925061060a565b6001836020036101000a038019825116818451168082178552505050505050905001915050600060405180830381855af49150503d806000811461068d576040519150601f19603f3d011682016040523d82523d6000602084013e610692565b606091505b5091509150816106ed576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040180806020018281038252602781526020018061087f6027913960400191505060405180910390fd5b866040518082805190602001908083835b6020831061072157805182526020820191506020810190506020830392506106fe565b6001836020036101000a0380198251168184511680821785525050505050509050019150506040518091039020886040518082805190602001908083835b60208310610782578051825260208201915060208101905060208303925061075f565b6001836020036101000a03801982511681845116808217855250505050505090500191505060405180910390207f6a739057159b3f3e2efcba00d44b0fa47de56972ed8776a2da7682bcf7c67de1876040518080602001828103825283818151815260200191508051906020019080838360005b838110156108115780820151818401526020810190506107f6565b50505050905090810190601f16801561083e5780820380516001836020036101000a031916815260200191505b509250505060405180910390a3809350505050949350505050565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff168156fe4572726f722063616c6c696e67207365727669636520636f6e74726163742066756e6374696f6ea26469706673582212207ff67ea2b4b9781fda166061f0c242b562fc5caef5dac685878272eb049d75cb64736f6c63430006060033'
coin_contract = '608060405234801561001057600080fd5b50336000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff1602179055506104c3806100606000396000f3fe608060405234801561001057600080fd5b506004361061004c5760003560e01c8063075461721461005157806327e235e31461009b57806340c10f19146100f3578063d0679d3414610141575b600080fd5b61005961018f565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b6100dd600480360360208110156100b157600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff1690602001909291905050506101b4565b6040518082815260200191505060405180910390f35b61013f6004803603604081101561010957600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803590602001909291905050506101cc565b005b61018d6004803603604081101561015757600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff1690602001909291908035906020019092919050505061029b565b005b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b60016020528060005260406000206000915090505481565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff161461022557600080fd5b789f4f2726179a224501d762422c946590d91000000000000000811061024a57600080fd5b80600160008473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600082825401925050819055505050565b600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054811115610350576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260158152602001807f496e73756666696369656e742062616c616e63652e000000000000000000000081525060200191505060405180910390fd5b80600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000828254039250508190555080600160008473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600082825401925050819055507f3990db2d31862302a685e8086b5755072a6e2b5b780af1ee81ece35ee3cd3345338383604051808473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001828152602001935050505060405180910390a1505056fea26469706673582212201aa2c68fa7da001a994c3d3a4892af7de19c6b2b85d2fe3df3c8dbbc11ef8acf64736f6c63430006060033'


def trace(func):
    """
    A decorator for tracing methods' begin/end execution points
    """

    def tracer(*args, **kwargs):
        name = func.__name__
        print('\tEntering "{}"'.format(name))
        result = func(*args, **kwargs)
        print('\tLeaving "{}"'.format(name))
        return result

    return tracer


@trace
def send_transaction_and_print_status(transaction):
    global hex_hash
    hex_hash = binascii.hexlify(IrohaCrypto.hash(transaction))
    print('Transaction hash = {}, creator = {}'.format(
        hex_hash, transaction.payload.reduced_payload.creator_account_id))
    net.send_tx(transaction)
    for status in net.tx_status_stream(transaction):
        print(status)


@trace
def call_engine():
    tx = iroha.transaction([
        iroha.command('CallEngine', caller=ADMIN_ACCOUNT_ID,
                      input=coin_contract)
    ])
    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)

@trace
def getEngineReceipts():
    query = iroha.query('GetEngineReceipts', tx_hash="48edc171bd7c67ee0a11666298c56f3c3d8ec9a07ab7825e9916930f9cc5e68a".upper())
    IrohaCrypto.sign_query(query, ADMIN_PRIVATE_KEY)
    response = net.send_query(query)
    print(response)


call_engine()
getEngineReceipts()
print('done')
