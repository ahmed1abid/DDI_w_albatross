// SPDX-License-Identifier: MIT
pragma solidity 0.8.23;

contract VMController {

    struct VMConfig {
        bool exists;
        string vmName;
        string remote;
        string hook;
        string ipv4;
        string ipv4Gateway;
        uint256 port;
        bool tls;
        string sshKey;
        bool signed;
    }

    mapping(string => VMConfig) public vmConfigs;

    event VMCreated(string vmName);
    event VMDestroyed(string vmName);
    event VMSigned(string vmName);

    function createVM(
        string memory vmName,
        string memory remote,
        string memory hook,
        string memory ipv4,
        string memory ipv4Gateway,
        uint256 port,
        bool tls,
        string memory sshKey
    ) external {
        require(!vmConfigs[vmName].exists, "VM already exists");

        vmConfigs[vmName] = VMConfig(
            true,
            vmName,
            remote,
            hook,
            ipv4,
            ipv4Gateway,
            port,
            tls,
            sshKey,
            false
        );

        emit VMCreated(vmName);
    }

    function destroyVM(string memory vmName) external {
        require(vmConfigs[vmName].exists, "VM does not exist");

        delete vmConfigs[vmName];

        emit VMDestroyed(vmName);
    }

    function signVM(string memory vmName) external {
        require(!vmConfigs[vmName].signed, "VM already signed");

        vmConfigs[vmName].signed = true;

        emit VMSigned(vmName);
    }

    function isVMSigned(string memory vmName) external view returns (bool) {
        return vmConfigs[vmName].signed;
    }
}
