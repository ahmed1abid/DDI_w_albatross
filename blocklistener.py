from web3 import Web3
import threading
import time
import json
import asyncio
from certif2 import Certif

# Paramètres généraux
web3_provider_url = 'http://127.0.0.1:8545'  # URL du fournisseur Web3
DEBUG_MODE = True  # Mode de débogage (True pour activer)

# Web3 connection
web3 = Web3(Web3.HTTPProvider(web3_provider_url))

# ABI et adresse du contrat intelligent
with open("./build/contracts/VMController.json", "r") as json_file:
    contract_data = json.load(json_file)
contract_address = "0xCfEB869F69431e42cdB54A4F4f105C19C080A601"  # Adresse du contrat
contract_abi = contract_data["abi"]  # ABI du contrat

# Instance du contrat intelligent
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Clé privée Ethereum pour interagir avec le contrat (Note: Remplacer cette clé par la clé appropriée pour votre client)
account_private_key = '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'

# Fonction pour imprimer des messages de débogage
def debug_print(message):
    if DEBUG_MODE:
        print("[DEBUG]:", message)

async def sign_vm(vmName):
    await Certif.sign_vm()
    debug_print(f"Signing VM: {vmName}")

def create_certificate(vmName):
    Certif.create_unikernel()
    debug_print(f"Creating certificate for VM: {vmName}")


def destroy_vm(vmName):
    Certif.Destroy_vm()
    debug_print(f"Destroying VM: {vmName}")

def event_listener():
    def handle_event(event):
        # Extraire les informations pertinentes de l'événement
        event_name = event['event']
        vmName = event['args']['vmName'] if 'args' in event and 'vmName' in event['args'] else None
        debug_print(f"Received event: {event_name}, VM name: {vmName}")
        if vmName:
            # Exécuter des actions en fonction de l'événement
            if event_name == 'VMCreated':
                create_certificate(vmName)
            elif event_name == 'VMDestroyed':
                destroy_vm(vmName)
            elif event_name == 'VMSigned':
                sign_vm(vmName)

    # Souscrire à des événements spécifiques
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

# Démarrer l'écouteur d'événements dans un thread séparé
listener_thread = threading.Thread(target=event_listener)
listener_thread.start()

# Garder le thread principal en cours d'exécution
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Listener stopped.")
