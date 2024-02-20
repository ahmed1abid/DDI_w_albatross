# Decentralized Identity Management System (DDI) with Albatross

The Decentralized Identity Management System (DDI) utilizes the Albatross framework to manage certificates and interactions among users, issuers, and servers on the Ethereum blockchain.

## Setup and Installation

### Dependencies:
- Truffle v5.11.5
- Ganache v7.9.1
- Solidity - 0.8.23 (solc-js)
- Node v16.17.0
- Web3.js v1.10.0

1. **Clone the Repository**: 
   ```bash
   git clone https://github.com/your_username/DDI_w_albatross.git
   ```

2. **Install Dependencies and Build**:
   ```bash
   cd DDI_w_albatross
   make build
   pip3 install -requitements.txt
   ```

3. **Start Ganache**:
   ```bash
   make start-ganache
   ```

4. **Compile and Migrate Smart Contracts**:
   ```bash
   truffle migrate
   ```

## User CLI

The User Command Line Interface (CLI) provides commands for managing user accounts and virtual machines.

### Initialize User Account:
```bash
python3 cli_sol2.py
DIMS> init user
```
Follow the prompts to initialize the user account.

### Create VM:
```bash
DIMS> create vm
```

### Sign VM:
```bash
DIMS> sign vm
```

### Destroy VM:
```bash
DIMS> destroy vm
```

### Debug Mode:
To enable debug mode, add `--debug` as an argument:
```bash
DIMS> sign vm --debug
```

## Listener

To run the listener, execute:
```bash
python3 blocklistener.py
```

## Documentation

Refer to the provided documentation for setting up the Albatross environment and configuring the network setup. Ensure proper configuration of Ganache and the Albatross environment before executing commands. Review and update the provided commands and configurations based on your specific setup and requirements. Ensure that you run the listener too.

## Additional Notes

- Make sure to configure Ganache and the Albatross environment properly before executing any commands.
- Review and update the provided commands and configurations according to your specific setup and requirements.
- Ensure that the listener is also running to monitor blockchain events and transactions effectively.