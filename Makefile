# Commands
TRUFFLE = truffle
GANACHE = ganache-cli

# Ethereum Smart Contracts directory
CONTRACTS_DIR = ./contracts

# Truffle Configuration
TRUFFLE_CONFIG = truffle-config.js

GANACHE_DB = nodesblockchain.json

# Start the Ganache development blockchain
start-ganache:
	$(GANACHE)  -d --gasLimit 900000000000 --miner.callGasLimit 90000000000 --db  $(GANACHE_DB)

# Deploy smart contracts using Truffle
deploy-contracts:
	$(TRUFFLE) migrate --reset --config $(TRUFFLE_CONFIG)

# Compile smart contracts using Truffle
compile-contracts:
	$(TRUFFLE) compile

# Build targets
build:
	sudo mkdir -p /run/albatross/util/
	sudo systemctl start albatross_daemon
	sudo systemctl start albatross_console
	sudo ip link add service-master address 02:00:00:00:00:01 type dummy
	sudo ip link set dev service-master  up
	sudo ip link add service type bridge
	sudo ip link set dev service-master master service
	sudo ip addr add 10.0.0.254/24 dev service
	sudo ip link set dev service up
	sudo sysctl -w net.ipv4.ip_forward=1
	sudo iptables -t nat -I POSTROUTING -s 10.0.0.0/24 -j MASQUERADE
	sudo iptables -t nat -I PREROUTING -p tcp --dport 8443 -j DNAT --to-destination 10.0.0.10

# Phony targets
.PHONY: run run-issuer install-python-deps start-ganache deploy-contracts compile-contracts build

