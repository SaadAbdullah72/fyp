// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @dev HalalChain Livestock Passport ERC-721 Standard Interfaces
 */

interface IERC165 {
    function supportsInterface(bytes4 interfaceId) external view returns (bool);
}

interface IERC721 is IERC165 {
    event Transfer(address indexed from, address indexed to, uint256 indexed tokenId);
    event Approval(address indexed owner, address indexed approved, uint256 indexed tokenId);
    event ApprovalForAll(address indexed owner, address indexed operator, bool approved);

    function balanceOf(address owner) external view returns (uint256 balance);
    function ownerOf(uint256 tokenId) external view returns (address owner);
    function safeTransferFrom(address from, address to, uint256 tokenId, bytes calldata data) external;
    function safeTransferFrom(address from, address to, uint256 tokenId) external;
    function transferFrom(address from, address to, uint256 tokenId) external;
    function approve(address to, uint256 tokenId) external;
    function setApprovalForAll(address operator, bool approved) external;
    function getApproved(uint256 tokenId) external view returns (address operator);
    function isApprovedForAll(address owner, address operator) external view returns (bool);
}

interface IERC721Metadata is IERC721 {
    function name() external view returns (string memory);
    function symbol() external view returns (string memory);
    function tokenURI(uint256 tokenId) external view returns (string memory);
}

interface IERC721Receiver {
    function onERC721Received(address operator, address from, uint256 tokenId, bytes calldata data) external returns (bytes4);
}

/**
 * @title HalalChainPassportNFT
 * @dev Enterprise ERC-721 Livestock Digital Passport & Halal Traceability Smart Contract.
 */
contract HalalChainPassportNFT is IERC165, IERC721, IERC721Metadata {
    string private _name;
    string private _symbol;
    address public contractOwner;
    uint256 public totalSupply;
    bool private _locked;

    struct LivestockIdentity {
        string cowId;             // Tag ID (e.g. HC-ETH-89412)
        string name;              // Animal Name (e.g. Bella)
        string breed;             // Breed (e.g. Sahiwal Cattle)
        string biometricHash;     // SHA-256 of 512-D Neural Vector
        string farmName;          // Registered Farm
        string location;          // Geographic Hub
        uint256 registeredAt;     // Timestamp
        address originalRegistrar; // Initial Wallet
        bool isHalalCertified;    // Halal Slaughter / Organic Status
    }

    struct MintParams {
        address to;
        string cowId;
        string animalName;
        string breed;
        string biometricHash;
        string farmName;
        string location;
        string metadataURI;
    }

    struct ProvenanceRecord {
        uint256 tokenId;
        string cowId;
        address from;
        address to;
        uint256 timestamp;
        uint256 priceWei;
        string certificateId;
        bytes32 txHash;
    }

    struct HealthRecord {
        uint256 timestamp;
        string recordType;
        string details;
        address veterinaryAddress;
    }

    // TokenId mappings
    mapping(uint256 => address) private _owners;
    mapping(address => uint256) private _balances;
    mapping(uint256 => address) private _tokenApprovals;
    mapping(address => mapping(address => bool)) private _operatorApprovals;
    mapping(uint256 => string) private _tokenURIs;

    // Livestock data mappings
    mapping(uint256 => LivestockIdentity) public passports;
    mapping(string => uint256) public cowIdToTokenId;
    mapping(string => uint256) public biometricHashToTokenId;
    mapping(uint256 => ProvenanceRecord[]) private _provenanceHistory;
    mapping(uint256 => HealthRecord[]) private _healthRecords;
    mapping(address => uint256[]) private _ownedTokens;

    // Events
    event PassportMinted(uint256 indexed tokenId, string indexed cowId, address indexed owner, string biometricHash);
    event OwnershipCertificateIssued(uint256 indexed tokenId, address indexed previousOwner, address indexed newOwner, string certificateId, uint256 priceWei);
    event HealthRecordAppended(uint256 indexed tokenId, string recordType, address veterinary);
    event HalalZibahStatusUpdated(uint256 indexed tokenId, bool isHalal, address inspector);

    modifier onlyOwner() {
        require(msg.sender == contractOwner, "Unauthorized: Only contract owner");
        _;
    }

    modifier nonReentrant() {
        require(!_locked, "ReentrancyGuard: reentrant call");
        _locked = true;
        _;
        _locked = false;
    }

    constructor() {
        _name = "HalalChain Livestock Digital Passport";
        _symbol = "HALAL";
        contractOwner = msg.sender;
    }

    function supportsInterface(bytes4 interfaceId) public pure override returns (bool) {
        return interfaceId == type(IERC721).interfaceId ||
               interfaceId == type(IERC721Metadata).interfaceId ||
               interfaceId == type(IERC165).interfaceId;
    }

    function name() public view override returns (string memory) {
        return _name;
    }

    function symbol() public view override returns (string memory) {
        return _symbol;
    }

    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(_owners[tokenId] != address(0), "Token does not exist");
        return _tokenURIs[tokenId];
    }

    function balanceOf(address owner) public view override returns (uint256) {
        require(owner != address(0), "Zero address query");
        return _balances[owner];
    }

    function ownerOf(uint256 tokenId) public view override returns (address) {
        address owner = _owners[tokenId];
        require(owner != address(0), "Token does not exist");
        return owner;
    }

    /**
     * @notice Mints an immutable Livestock Digital Passport NFT via struct params (prevents Stack-Too-Deep)
     */
    function mintPassport(MintParams calldata params) external nonReentrant returns (uint256) {
        require(params.to != address(0), "Cannot mint to zero address");
        require(bytes(params.cowId).length > 0, "Cow ID cannot be empty");
        require(bytes(params.biometricHash).length > 0, "Biometric hash required");
        require(cowIdToTokenId[params.cowId] == 0, "Cattle ID already registered on-chain");
        require(biometricHashToTokenId[params.biometricHash] == 0, "Biometric duplicate: Muzzle already registered");

        totalSupply++;
        uint256 newTokenId = totalSupply;

        _owners[newTokenId] = params.to;
        _balances[params.to]++;
        _tokenURIs[newTokenId] = params.metadataURI;
        _ownedTokens[params.to].push(newTokenId);

        passports[newTokenId] = LivestockIdentity({
            cowId: params.cowId,
            name: params.animalName,
            breed: params.breed,
            biometricHash: params.biometricHash,
            farmName: params.farmName,
            location: params.location,
            registeredAt: block.timestamp,
            originalRegistrar: msg.sender,
            isHalalCertified: false
        });

        cowIdToTokenId[params.cowId] = newTokenId;
        biometricHashToTokenId[params.biometricHash] = newTokenId;

        _provenanceHistory[newTokenId].push(ProvenanceRecord({
            tokenId: newTokenId,
            cowId: params.cowId,
            from: address(0),
            to: params.to,
            timestamp: block.timestamp,
            priceWei: 0,
            certificateId: string(abi.encodePacked("GENESIS-", params.cowId)),
            txHash: bytes32(0)
        }));

        emit Transfer(address(0), params.to, newTokenId);
        emit PassportMinted(newTokenId, params.cowId, params.to, params.biometricHash);

        return newTokenId;
    }

    /**
     * @notice Helper mint overload for single-call execution
     */
    function registerPassport(
        address to,
        string calldata cowId,
        string calldata animalName,
        string calldata breed,
        string calldata biometricHash,
        string calldata farmName,
        string calldata location,
        string calldata metadataURI
    ) external returns (uint256) {
        return this.mintPassport(MintParams({
            to: to,
            cowId: cowId,
            animalName: animalName,
            breed: breed,
            biometricHash: biometricHash,
            farmName: farmName,
            location: location,
            metadataURI: metadataURI
        }));
    }

    /**
     * @notice ERC-721 Standard safeTransferFrom with Certificate Issuance
     */
    function transferPassportWithCertificate(
        address to,
        uint256 tokenId,
        uint256 priceWei,
        string calldata certificateId
    ) external payable nonReentrant {
        address currentOwner = ownerOf(tokenId);
        require(msg.sender == currentOwner || isApprovedForAll(currentOwner, msg.sender) || getApproved(tokenId) == msg.sender, "Transfer unauthorized");
        require(to != address(0), "Cannot transfer to zero address");
        require(to != currentOwner, "Recipient is already the current owner");

        if (priceWei > 0) {
            require(msg.value >= priceWei, "Insufficient payment forwarded");
            (bool success, ) = payable(currentOwner).call{value: msg.value}("");
            require(success, "Payment forwarding failed");
        }

        _transfer(currentOwner, to, tokenId);

        string memory cId = bytes(certificateId).length > 0 ? certificateId : "CERT-PENDING";
        _provenanceHistory[tokenId].push(ProvenanceRecord({
            tokenId: tokenId,
            cowId: passports[tokenId].cowId,
            from: currentOwner,
            to: to,
            timestamp: block.timestamp,
            priceWei: priceWei,
            certificateId: cId,
            txHash: bytes32(0)
        }));

        emit OwnershipCertificateIssued(tokenId, currentOwner, to, cId, priceWei);
    }

    function _transfer(address from, address to, uint256 tokenId) internal {
        require(ownerOf(tokenId) == from, "Transfer from incorrect owner");
        _balances[from]--;
        _balances[to]++;
        _owners[tokenId] = to;
        delete _tokenApprovals[tokenId];

        _removeTokenFromOwnerList(from, tokenId);
        _ownedTokens[to].push(tokenId);

        emit Transfer(from, to, tokenId);
    }

    function _removeTokenFromOwnerList(address from, uint256 tokenId) internal {
        uint256[] storage list = _ownedTokens[from];
        for (uint256 i = 0; i < list.length; i++) {
            if (list[i] == tokenId) {
                list[i] = list[list.length - 1];
                list.pop();
                break;
            }
        }
    }

    function safeTransferFrom(address from, address to, uint256 tokenId, bytes calldata data) external override {
        address currentOwner = ownerOf(tokenId);
        require(msg.sender == currentOwner || isApprovedForAll(currentOwner, msg.sender) || getApproved(tokenId) == msg.sender, "Transfer unauthorized");
        _transfer(from, to, tokenId);
        require(_checkOnERC721Received(from, to, tokenId, data), "Transfer to non ERC721Receiver");
    }

    function safeTransferFrom(address from, address to, uint256 tokenId) external override {
        address currentOwner = ownerOf(tokenId);
        require(msg.sender == currentOwner || isApprovedForAll(currentOwner, msg.sender) || getApproved(tokenId) == msg.sender, "Transfer unauthorized");
        _transfer(from, to, tokenId);
        require(_checkOnERC721Received(from, to, tokenId, ""), "Transfer to non ERC721Receiver");
    }

    function transferFrom(address from, address to, uint256 tokenId) public override {
        address currentOwner = ownerOf(tokenId);
        require(msg.sender == currentOwner || isApprovedForAll(currentOwner, msg.sender) || getApproved(tokenId) == msg.sender, "Transfer unauthorized");
        _transfer(from, to, tokenId);
    }

    function approve(address to, uint256 tokenId) public override {
        address owner = ownerOf(tokenId);
        require(msg.sender == owner || isApprovedForAll(owner, msg.sender), "Not authorized to approve");
        _tokenApprovals[tokenId] = to;
        emit Approval(owner, to, tokenId);
    }

    function setApprovalForAll(address operator, bool approved) public override {
        require(operator != msg.sender, "Approve to caller");
        _operatorApprovals[msg.sender][operator] = approved;
        emit ApprovalForAll(msg.sender, operator, approved);
    }

    function getApproved(uint256 tokenId) public view override returns (address) {
        require(_owners[tokenId] != address(0), "Token does not exist");
        return _tokenApprovals[tokenId];
    }

    function isApprovedForAll(address owner, address operator) public view override returns (bool) {
        return _operatorApprovals[owner][operator];
    }

    function _checkOnERC721Received(address from, address to, uint256 tokenId, bytes memory data) private returns (bool) {
        if (to.code.length > 0) {
            try IERC721Receiver(to).onERC721Received(msg.sender, from, tokenId, data) returns (bytes4 retval) {
                return retval == IERC721Receiver.onERC721Received.selector;
            } catch {
                return false;
            }
        }
        return true;
    }

    // View Functions
    function getPassport(uint256 tokenId) external view returns (LivestockIdentity memory) {
        require(_owners[tokenId] != address(0), "Token does not exist");
        return passports[tokenId];
    }

    function getPassportByCowId(string calldata cowId) external view returns (LivestockIdentity memory, uint256) {
        uint256 tokenId = cowIdToTokenId[cowId];
        require(tokenId != 0, "Animal not registered");
        return (passports[tokenId], tokenId);
    }

    function getProvenanceHistory(uint256 tokenId) external view returns (ProvenanceRecord[] memory) {
        return _provenanceHistory[tokenId];
    }

    function getTokensByOwner(address owner) external view returns (uint256[] memory) {
        return _ownedTokens[owner];
    }

    function appendHealthRecord(uint256 tokenId, string calldata recordType, string calldata details) external {
        require(_owners[tokenId] != address(0), "Token does not exist");
        _healthRecords[tokenId].push(HealthRecord({
            timestamp: block.timestamp,
            recordType: recordType,
            details: details,
            veterinaryAddress: msg.sender
        }));
        emit HealthRecordAppended(tokenId, recordType, msg.sender);
    }

    function setHalalStatus(uint256 tokenId, bool isHalal) external onlyOwner {
        require(_owners[tokenId] != address(0), "Token does not exist");
        passports[tokenId].isHalalCertified = isHalal;
        emit HalalZibahStatusUpdated(tokenId, isHalal, msg.sender);
    }
}
