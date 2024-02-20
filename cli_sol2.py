import json
from web3 import Web3
from User import User
import asyncio
import requests
from certif2 import Certif

# Initialize user variables
name = "DIMS"
wallet_file = None
user = None
ssn = None

# Connect to the local Ethereum node
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545', request_kwargs={'timeout': 10000}))

# Load contract ABI and address from JSON file
with open("./build/contracts/DataRegistry.json", "r") as json_file:
    contract_data = json.load(json_file)

# Extract contract ABI and address
contract_abi_1 = contract_data["abi"]
contract_address_1 = '0x254dffcd3277C0b1660F6d42EFbB754edaBAbC2B'
private_key_1 = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"

# Create a contract instance
data_registry = w3.eth.contract(address=contract_address_1, abi=contract_abi_1)

# Load contract ABI and address
with open("./build/contracts/VMController.json", "r") as json_file:
    contract_data = json.load(json_file)

contract_address = "0xCfEB869F69431e42cdB54A4F4f105C19C080A601"
contract_abi = contract_data["abi"]
vm_controller = w3.eth.contract(address=contract_address, abi=contract_abi)

# Set a sample user address for testing
user_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"


def initialize_user():
    """
    Initialize user data.
    """
    global name, wallet_file, user, ssn

    # Get user input
    print("Enter your name: ", end="")
    name = input()
    print(f"Hello {name}")

    print("Enter your ssn: ", end="")
    ssn = int(input())
    print(f"Your SSN: {ssn}")

    print("Enter your data: ", end="")
    data = input()

    try:
        # Create User instance and encrypt data
        user = User(name=name, ssn=ssn, data=data)
        user.encrypt_data()
        print("Wallet Loaded")

    except Exception as e:
        print("Error in loading wallet")
        raise e


async def send_transaction_async(chunk, nonce, gas_price, gas_limit, chain_id):
    """
    Asynchronously send a transaction to the blockchain.

    Args:
        chunk (bytes): Data chunk to send.
        nonce (int): Transaction nonce.
        gas_price (int): Gas price for the transaction.
        gas_limit (int): Gas limit for the transaction.
        chain_id (int): Chain ID.

    Returns:
        dict: Response from the blockchain node.
    """
    transaction = {
        'to': user_address,
        'gas': gas_limit,
        'gasPrice': gas_price,
        'nonce': nonce,
        'data': chunk.hex(),
        'chainId': chain_id,
    }
    signed_transaction = w3.eth.account.sign_transaction(transaction, private_key_1)
    payload = {
        'jsonrpc': '2.0',
        'method': 'eth_sendRawTransaction',
        'params': [signed_transaction.rawTransaction.hex()],
        'id': 1,
    }
    response = requests.post('http://127.0.0.1:8545', json=payload)
    return response.json().get('result')


async def send_file_to_blockchain(file_path):
    """
    Send a file to the blockchain.

    Args:
        file_path (str): Path to the file to send.
    """
    if not file_path:
        print("File path not provided.")
        return

    try:
        with open(file_path, 'rb') as file:
            file_content = file.read()

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return

    nonce = w3.eth.get_transaction_count(user_address)
    gas_price = w3.eth.gas_price
    gas_limit = 90000000  # Adjust as needed
    chain_id = w3.eth.chain_id

    chunk_size = len(file_content) // 100
    tasks = []

    for i in range(100):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i < 99 else len(file_content)
        chunk = file_content[start:end]

        tasks.append(send_transaction_async(chunk, nonce + i, gas_price, gas_limit, chain_id))

    responses = await asyncio.gather(*tasks)

    await wait_for_transactions_mined(responses)

    print("All transactions sent to the blockchain successfully.")


async def wait_for_transactions_mined(tx_hashes):
    """
    Wait for transactions to be mined.

    Args:
        tx_hashes (list): List of transaction hashes to monitor.
    """
    for tx_hash in tx_hashes:
        if tx_hash is None:
            continue

        while True:
            try:
                receipt = w3.eth.get_transaction_receipt(tx_hash)
                if receipt and receipt['blockNumber']:
                    print(f"Transaction {tx_hash} mined in block {receipt['blockNumber']}")
                    break
                await asyncio.sleep(1)
            except Exception as e:
                print(f"Error getting receipt for {tx_hash}: {e}")
                await asyncio.sleep(1)


def is_contract_deployed(address):
    """
    Check if a contract is deployed at the given address.

    Args:
        address (str): Address of the contract to check.

    Returns:
        bool: True if a contract is deployed, False otherwise.
    """
    try:
        code = w3.eth.get_code(address)
        return code and code != "0x"
    except Exception as e:
        print(f"Error checking if contract is deployed: {e}")
        return False


async def get_latest_transaction_hashes():
    """
    Get the latest transaction hashes.

    Returns:
        list: List of transaction hashes.
    """
    try:
        transaction_hashes = []

        for latest_block_number in range(0, 101):
            block = w3.eth.get_block(latest_block_number, True)

            if block and 'transactions' in block:
                transaction_hashes.extend([tx['hash'].hex() for tx in block['transactions']])
            else:
                print(f"No transactions found in block {latest_block_number}.")

        return transaction_hashes

    except Exception as e:
        print(f"Error while retrieving transactions: {e}")
        return []


async def get_file_from_blockchain():
    """
    Get a file from the blockchain.
    """
    transaction_hashes = await get_latest_transaction_hashes()
    for tx_hash in transaction_hashes:
        payload = {
            'jsonrpc': '2.0',
            'method': 'eth_getTransactionByHash',
            'params': [tx_hash],
            'id': 1,
        }

        try:
            response = requests.post('http://127.0.0.1:8545', json=payload)
            response.raise_for_status()
            result = response.json().get('result')

            if result:
                input_data = result.get('input')
                decoded_input_data = bytes.fromhex(input_data[2:])
                file_path = "./unipi.hvt"  # Adjust path as needed

                with open(file_path, "ab") as file:
                    file.write(decoded_input_data)

            else:
                print(f"Transaction {tx_hash} not found.")

        except requests.exceptions.RequestException as e:
            print(f"Error during JSON-RPC request: {e}")


async def Destroy_vm(vm_name="unipi"):
    """
    Destroy a virtual machine.

    Args:
        vm_name (str): Name of the virtual machine.
    """
    global w3, vm_controller, user_address

    nonce = w3.eth.get_transaction_count(user_address)
    chain_id = w3.eth.chain_id

    transaction = vm_controller.functions.destroyVM(
        vm_name).build_transaction({
        'gas': 2000000,
        'gasPrice': 20000000000,
        'from': user_address,
        'nonce': nonce,
        'chainId': chain_id
    })

    tx_hash = w3.eth.send_transaction(transaction)
    print(f"VM is getting destroyed. Transaction Hash: {tx_hash.hex()}")


async def Create_vm_with_unipi(vm_name, hook, ipv4, ipv4_gateway, port, tls):
    """
    Create a virtual machine with UNIPI.

    Args:
        vm_name (str): Name of the virtual machine.
        hook (str): Hook for the virtual machine.
        ipv4 (str): IPv4 address for the virtual machine.
        ipv4_gateway (str): IPv4 gateway for the virtual machine.
        port (int): Port for the virtual machine.
        tls (bool): Whether to enable TLS for the virtual machine.
    """
    await get_file_from_blockchain()
    global w3, vm_controller, user_address

    nonce = w3.eth.get_transaction_count(user_address)
    chain_id = w3.eth.chain_id

    transaction = vm_controller.functions.createVM(
        vm_name,
        "https://github.com/ahmed1abid/Test.git",
        hook,
        ipv4,
        ipv4_gateway,
        port,
        tls,
        "ed25519:2JueTxGu7icIG6jpfFDl4AEr4L6zTUbMkS+e2vW4B/8="
    ).build_transaction({
        'gas': 2000000,
        'gasPrice': 20000000000,
        'from': user_address,
        'nonce': nonce,
        'chainId': chain_id
    })

    tx_hash = w3.eth.send_transaction(transaction)
    print(f"VM creation initiated. Transaction Hash: {tx_hash.hex()}")


async def sign_vm(vm_name="unipi", debug_mode=False):
    """
    Sign a virtual machine.

    Args:
        vm_name (str): Name of the virtual machine.
        debug_mode (bool): Whether to enable debug mode.
    """
    global w3, vm_controller, user_address

    nonce = w3.eth.get_transaction_count(user_address)
    chain_id = w3.eth.chain_id

    transaction = vm_controller.functions.signVM(
        vm_name).build_transaction({
        'gas': 2000000,
        'gasPrice': 20000000000,
        'from': user_address,
        'nonce': nonce,
        'chainId': chain_id
    })

    tx_hash = w3.eth.send_transaction(transaction)
    print(f"VM signement initiated. Transaction Hash: {tx_hash.hex()}")

    if debug_mode:
        print("Debug mode enabled.")


if __name__ == "__main__":
    # Enter the main loop
    while True:
        print(f"# {name}> ", end="")
        inp_list = input().split(' ')

        # Handle user commands
        if inp_list[0] in ['initialize', 'init']:
            if inp_list[1] in ['user']:
                initialize_user()

        elif inp_list[0] in ['destroy']:
            if inp_list[1] in ['vm']:
                asyncio.run(Destroy_vm("unipi"))
            else:
                print("There is a problem with the VM: either it's not created or we don't have access to delete it.")

        elif inp_list[0] in ['send', 'store', 'upload']:
            if inp_list[1] in ['data']:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(send_file_to_blockchain('./unipi.hvt'))  # Adjust path as needed
            else:
                print("User address is not set. Make sure to set it to your Ethereum address.")

        elif inp_list[0] in ['get']:
            if inp_list[1] in ['data']:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(get_file_from_blockchain())
        elif inp_list[0] in ['sign']:
            if inp_list[1] in ['vm']:
                debug_mode = '--debug' in inp_list  # Check if debug mode is enabled
                asyncio.run(sign_vm("unipi", debug_mode=debug_mode))
        elif inp_list[0] in ['start']:
            if inp_list[1] in ['tls']:
                asyncio.run(Certif.server_start_endpoint())
        elif inp_list[0] in ['add']:
            if inp_list[1] in ['policy']:
                asyncio.run(Certif.user_add_policy())
        elif inp_list[0] in ['sign']:
            if inp_list[1] in ['certif']:
                Certif.sign_certificate_request()
        elif inp_list[0] in ['create']:
            if inp_list[1] in ['vm']:
                asyncio.run(Create_vm_with_unipi("unipi", "/updatewebhook", "10.0.0.10/24", "10.0.0.254", 8443, True))
            else:
                print("User address is not set. Make sure to set it to your Ethereum address.")
