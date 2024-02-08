// SPDX-License-Identifier: MIT
pragma solidity 0.8.23;

contract DataRegistry {

    bytes public storedFileData;
    event FileStored(address indexed sender, uint256 fileContentLength);

    function storeFile(bytes memory fileContent) public {
        storedFileData = abi.encodePacked(storedFileData, fileContent);
        emit FileStored(msg.sender, fileContent.length);
    }

    function getStoredFileData() public view returns (address, uint256) {
        return (msg.sender, storedFileData.length);
    }

    function getStoredFile() public view returns (bytes memory) {
        return storedFileData;
    }
}
