from web3 import Web3
import threading
import time
import json
import asyncio
from certif2 import Certif

# Web3 connection
web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

# Smart Contract ABI and Address
with open("./build/contracts/VMController.json", "r") as json_file:
    contract_data = json.load(json_file)
contract_address = "0xCfEB869F69431e42cdB54A4F4f105C19C080A601"
contract_abi = contract_data["abi"]

# Smart Contract instance
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Ethereum account to interact with the contract
account_private_key = '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'

async def sign_vm(vmName):
    await Certif.sign_vm()
    print(f"Signing VM: {vmName}")

def create_certificate(vmName):
    Certif.client_create_remote_unipi()
    print(f"Creating certificate for VM: {vmName}")

def certificate(vmName):
    Certif.client_create_remote_unipi() 
    print(f"Certifying VM: {vmName}")

def destroy_vm(vmName):
    Certif.Destroy_vm()
    print(f"Destroying VM: {vmName}")

def event_listener():
    def handle_event(event):
        # Extract relevant information from the event
        event_name = event['event']
        vmName = event['args']['vmName'] if 'args' in event and 'vmName' in event['args'] else None
        print(f"Received event: {event_name}, VM name: {vmName}")
        if vmName:
            # Perform actions based on the event
            if event_name == 'VMCreated':
                create_certificate(vmName)
            elif event_name == 'VMDestroyed':
                destroy_vm(vmName)
            elif event_name == 'VMSigned':
                sign_vm(vmName)

    # Subscribe to specific events
    event_filter_vm_created = contract.events.VMCreated.create_filter(fromBlock=101, toBlock="latest")
    event_filter_vm_destroyed = contract.events.VMDestroyed.create_filter(fromBlock=101, toBlock="latest")
    event_filter_vm_signed = contract.events.VMSigned.create_filter(fromBlock=101, toBlock="latest")

    while True:
        for event in event_filter_vm_created.get_new_entries():
            handle_event(event)

        for event in event_filter_vm_destroyed.get_new_entries():
            handle_event(event)

        for event in event_filter_vm_signed.get_new_entries():
            handle_event(event)

        time.sleep(1)

# Start the event listener in a separate thread
listener_thread = threading.Thread(target=event_listener)
listener_thread.start()

# Keep the main thread running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Listener stopped.")
