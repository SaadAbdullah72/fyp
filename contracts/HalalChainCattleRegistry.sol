// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title HalalChainCattleRegistry
 * @dev Immutable Bovine Biometric Identity & Halal Traceability Registry for Ethereum Sepolia Testnet.
 * Features:
 *  - ArcFace 512-D Biometric Fingerprint Anchoring (Anti-Duplicate Enforcement)
 *  - Decentralized Ownership Records & History
 *  - Wallet-Based Cattle Enumeration (Search by Ethereum Address)
 *  - P2P Ownership Transfers with Sepolia ETH Payment Settlement
 */
contract HalalChainCattleRegistry {
    address public contractDeployer;

    struct CattleRecord {
        string cowId;             // Unique Identifier (e.g., HC-SEP-89241)
        string name;              // Animal Name (e.g. Bella)
        string breed;             // Cattle Breed (e.g. Sahiwal Cattle)
        string biometricHash;     // Cryptographic SHA-256 / Keccak256 hash of 512-D master embedding
        string farmName;          // Registered Farm / Ranch Name
        string location;          // Farm Location / Coordinates
        address currentOwner;     // Current registered Ethereum owner address
        uint256 registeredAt;     // Timestamp of initial enrollment
        uint256 lastTransferredAt;// Timestamp of most recent transfer
        bool isRegistered;        // Existence verification flag
    }

    struct OwnershipTransferRecord {
        string cowId;
        address from;
        address to;
        uint256 priceWei;         // Amount in Wei (0 if gift/assignment)
        uint256 timestamp;
        string currency;          // "ETH"
    }

    // Mapping: cowId => CattleRecord
    mapping(string => CattleRecord) private cattleRecords;

    // Mapping: biometricHash => isRegistered (Tier-2 Anti-Duplicate Protection)
    mapping(string => bool) private registeredBiometrics;
    mapping(string => string) private biometricToCowId;

    // Mapping: ownerAddress => list of cowIds owned
    mapping(address => string[]) private ownerCattleList;

    // Mapping: cowId => history of all transfers
    mapping(string => OwnershipTransferRecord[]) private cattleTransferHistory;

    // Global list of all registered cattle IDs
    string[] public allCattleIds;

    // Reentrancy lock
    bool private locked;
    modifier nonReentrant() {
        require(!locked, "ReentrancyGuard: reentrant call");
        locked = true;
        _;
        locked = false;
    }

    // Events
    event CattleRegistered(
        string indexed cowId,
        string name,
        string breed,
        string biometricHash,
        address indexed owner,
        uint256 timestamp
    );

    event CattleTransferred(
        string indexed cowId,
        address indexed from,
        address indexed to,
        uint256 priceWei,
        uint256 timestamp
    );

    constructor() {
        contractDeployer = msg.sender;
    }

    /**
     * @notice Register a verified bovine biometric passport to Ethereum Sepolia.
     * Enforces anti-duplicate check on the biometric hash.
     */
    function registerCattle(
        string memory _cowId,
        string memory _name,
        string memory _breed,
        string memory _biometricHash,
        string memory _farmName,
        string memory _location
    ) external returns (bool) {
        require(bytes(_cowId).length > 0, "Error: Cow ID cannot be empty");
        require(!cattleRecords[_cowId].isRegistered, "Error: Cow ID already exists on-chain");
        require(!registeredBiometrics[_biometricHash], "Security Alert: Biometric hash already registered! Duplicate cattle fraud detected.");

        cattleRecords[_cowId] = CattleRecord({
            cowId: _cowId,
            name: _name,
            breed: _breed,
            biometricHash: _biometricHash,
            farmName: _farmName,
            location: _location,
            currentOwner: msg.sender,
            registeredAt: block.timestamp,
            lastTransferredAt: block.timestamp,
            isRegistered: true
        });

        registeredBiometrics[_biometricHash] = true;
        biometricToCowId[_biometricHash] = _cowId;
        ownerCattleList[msg.sender].push(_cowId);
        allCattleIds.push(_cowId);

        emit CattleRegistered(_cowId, _name, _breed, _biometricHash, msg.sender, block.timestamp);
        return true;
    }

    /**
     * @notice Direct P2P ownership transfer by current owner (No payment).
     */
    function transferOwnership(
        string memory _cowId,
        address _newOwner
    ) external returns (bool) {
        require(cattleRecords[_cowId].isRegistered, "Cattle not found");
        require(cattleRecords[_cowId].currentOwner == msg.sender, "Unauthorized: Only current owner can transfer");
        require(_newOwner != address(0), "Invalid recipient address");
        require(_newOwner != msg.sender, "Recipient cannot be current owner");

        _executeTransfer(_cowId, msg.sender, _newOwner, 0);
        return true;
    }

    /**
     * @notice Ownership transfer with ETH payment settlement on Sepolia.
     * Buyer or intermediary sends ETH value with the transaction.
     */
    function transferCattleWithPayment(
        string memory _cowId,
        address payable _newOwner
    ) external payable nonReentrant returns (bool) {
        require(cattleRecords[_cowId].isRegistered, "Cattle not found");
        address currentOwner = cattleRecords[_cowId].currentOwner;
        require(currentOwner == msg.sender, "Unauthorized: Only current owner can initiate transfer");
        require(_newOwner != address(0), "Invalid recipient address");
        require(_newOwner != currentOwner, "Recipient cannot be current owner");

        // Forward payment to seller if value provided
        if (msg.value > 0) {
            (bool sent, ) = payable(currentOwner).call{value: msg.value}("");
            require(sent, "Failed to send ETH payment to seller");
        }

        _executeTransfer(_cowId, currentOwner, _newOwner, msg.value);
        return true;
    }

    /**
     * @dev Internal transfer logic updating records and enumeration arrays.
     */
    function _executeTransfer(
        string memory _cowId,
        address _from,
        address _to,
        uint256 _priceWei
    ) internal {
        // Update cattle owner
        cattleRecords[_cowId].currentOwner = _to;
        cattleRecords[_cowId].lastTransferredAt = block.timestamp;

        // Remove from old owner's array
        _removeCowFromOwnerList(_from, _cowId);

        // Add to new owner's array
        ownerCattleList[_to].push(_cowId);

        // Append to immutable history
        cattleTransferHistory[_cowId].push(OwnershipTransferRecord({
            cowId: _cowId,
            from: _from,
            to: _to,
            priceWei: _priceWei,
            timestamp: block.timestamp,
            currency: "ETH"
        }));

        emit CattleTransferred(_cowId, _from, _to, _priceWei, block.timestamp);
    }

    function _removeCowFromOwnerList(address _owner, string memory _cowId) internal {
        string[] storage list = ownerCattleList[_owner];
        for (uint256 i = 0; i < list.length; i++) {
            if (keccak256(bytes(list[i])) == keccak256(bytes(_cowId))) {
                list[i] = list[list.length - 1];
                list.pop();
                break;
            }
        }
    }

    // ==============================================================
    // VIEW / AUDIT FUNCTIONS
    // ==============================================================

    /**
     * @notice Get cattle details by Cow ID
     */
    function getCattle(string memory _cowId) external view returns (CattleRecord memory) {
        require(cattleRecords[_cowId].isRegistered, "Cattle record not found on blockchain");
        return cattleRecords[_cowId];
    }

    /**
     * @notice Get list of all cattle IDs owned by an Ethereum address
     */
    function getCattleByOwner(address _owner) external view returns (string[] memory) {
        return ownerCattleList[_owner];
    }

    /**
     * @notice Get full transfer history & provenance log of a cow
     */
    function getTransferHistory(string memory _cowId) external view returns (OwnershipTransferRecord[] memory) {
        require(cattleRecords[_cowId].isRegistered, "Cattle not found");
        return cattleTransferHistory[_cowId];
    }

    /**
     * @notice Check whether a biometric fingerprint hash is already registered
     */
    function isBiometricRegistered(string memory _biometricHash) external view returns (bool, string memory) {
        return (registeredBiometrics[_biometricHash], biometricToCowId[_biometricHash]);
    }

    /**
     * @notice Total registered cattle count
     */
    function getTotalCattleCount() external view returns (uint256) {
        return allCattleIds.length;
    }
}
