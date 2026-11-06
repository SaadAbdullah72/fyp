// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title HalalChainSupplyChainMaster
 * @dev Optimized Enterprise Livestock Biometric NFT Passport & Halal Supply Chain Protocol.
 */
contract HalalChainSupplyChainMaster {
    string public name = "HalalChain Livestock Digital Passport";
    string public symbol = "HALAL";
    address public contractOwner;
    uint256 public totalSupply;
    uint256 public totalPackages;

    enum AnimalStatus { ALIVE_REGISTERED, IN_TRANSIT, RECEIVED_AT_SLAUGHTERHOUSE, SLAUGHTERED_HALAL, RETIRED }

    struct LivestockPassport {
        uint256 tokenId;
        string cowId;
        string biometricHash;
        string ipfsPassportCid;
        string animalName;
        string breed;
        string farmName;
        address currentOwner;
        AnimalStatus status;
        string currentCondition;
        uint256 registrationDate;
    }

    struct ProvenanceRecord {
        uint256 tokenId;
        address from;
        address to;
        uint256 timestamp;
        string condition;
        string transferPurpose;
        string certificateId;
    }

    struct Slaughterhouse {
        address wallet;
        string name;
        string licenseNumber;
        string location;
        bool isAuthorized;
    }

    struct Shopkeeper {
        address wallet;
        string shopName;
        string licenseNumber;
        string location;
        bool isAuthorized;
    }

    struct MeatPackage {
        uint256 packageId;
        string packageTag;
        uint256 parentTokenId;
        string parentCowId;
        string cutType;
        uint256 weightGrams;
        string batchId;
        address currentHolder;
        string retailShopName;
        bool isDeliveredToRetail;
    }

    // Storage Mappings
    mapping(uint256 => address) private _owners;
    mapping(address => uint256) private _balances;
    mapping(uint256 => address) private _tokenApprovals;
    mapping(address => mapping(address => bool)) private _operatorApprovals;

    mapping(uint256 => LivestockPassport) public passports;
    mapping(string => uint256) public cowIdToTokenId;
    mapping(address => Slaughterhouse) public authorizedSlaughterhouses;
    address[] public slaughterhouseList;
    mapping(address => Shopkeeper) public authorizedShopkeepers;
    address[] public shopkeeperList;

    mapping(uint256 => ProvenanceRecord[]) private _provenanceHistory;
    mapping(uint256 => MeatPackage) public meatPackages;
    mapping(string => uint256) public packageTagToPackageId;
    mapping(uint256 => uint256[]) private _parentToPackageIds;

    // Standard ERC-721 Events
    event Transfer(address indexed from, address indexed to, uint256 indexed tokenId);
    event Approval(address indexed owner, address indexed approved, uint256 indexed tokenId);
    event ApprovalForAll(address indexed owner, address indexed operator, bool approved);

    // Halal Supply Chain Events
    event PassportMinted(uint256 indexed tokenId, string indexed cowId, address indexed owner, string biometricHash);
    event SlaughterhouseAuthorized(address indexed slaughterhouse, string name, string licenseNumber);
    event SlaughterhouseRevoked(address indexed slaughterhouse);
    event ShopkeeperAuthorized(address indexed shopkeeper, string shopName, string licenseNumber);
    event ShopkeeperRevoked(address indexed shopkeeper);
    event CustodyTransferredToSlaughterhouse(uint256 indexed tokenId, string indexed cowId, address indexed slaughterhouse, string batchId);
    event HalalSlaughterSigned(uint256 indexed tokenId, string indexed cowId, address indexed slaughterhouse, uint256 timestamp, string certNumber);
    event MeatPackageCreated(uint256 indexed packageId, string packageTag, uint256 indexed parentTokenId, string cutType, uint256 weightGrams);
    event RetailDeliveryConfirmed(uint256 indexed packageId, string packageTag, address indexed retailer, string shopName, uint256 timestamp);
    event OwnershipTransferredWithCondition(uint256 indexed tokenId, address indexed from, address indexed to, string condition, string certId);

    modifier onlyOwner() {
        require(msg.sender == contractOwner, "Unauthorized: Only contract admin");
        _;
    }

    modifier onlyAuthorizedSlaughterhouse() {
        require(authorizedSlaughterhouses[msg.sender].isAuthorized, "Unauthorized: Caller is not a certified slaughterhouse");
        _;
    }

    modifier onlyAuthorizedShopkeeper() {
        require(authorizedShopkeepers[msg.sender].isAuthorized, "Unauthorized: Caller is not an authorized shopkeeper");
        _;
    }

    constructor() {
        contractOwner = msg.sender;
    }

    // ERC-721 Interface
    function balanceOf(address owner) external view returns (uint256) {
        require(owner != address(0), "Zero address query");
        return _balances[owner];
    }

    function ownerOf(uint256 tokenId) public view returns (address) {
        address owner = _owners[tokenId];
        require(owner != address(0), "Token does not exist");
        return owner;
    }

    // Admin Whitelisting
    function authorizeSlaughterhouse(
        address slaughterhouse,
        string calldata shName,
        string calldata licenseNumber,
        string calldata location
    ) external onlyOwner {
        require(slaughterhouse != address(0), "Invalid slaughterhouse address");
        if (!authorizedSlaughterhouses[slaughterhouse].isAuthorized) {
            slaughterhouseList.push(slaughterhouse);
        }
        authorizedSlaughterhouses[slaughterhouse] = Slaughterhouse({
            wallet: slaughterhouse,
            name: shName,
            licenseNumber: licenseNumber,
            location: location,
            isAuthorized: true
        });
        emit SlaughterhouseAuthorized(slaughterhouse, shName, licenseNumber);
    }

    function revokeSlaughterhouse(address slaughterhouse) external onlyOwner {
        require(authorizedSlaughterhouses[slaughterhouse].isAuthorized, "Not an authorized slaughterhouse");
        authorizedSlaughterhouses[slaughterhouse].isAuthorized = false;
        emit SlaughterhouseRevoked(slaughterhouse);
    }

    function getSlaughterhouseCount() external view returns (uint256) {
        return slaughterhouseList.length;
    }

    function isSlaughterhouseAuthorized(address slaughterhouse) external view returns (bool) {
        return authorizedSlaughterhouses[slaughterhouse].isAuthorized;
    }

    function authorizeShopkeeper(
        address shopkeeper,
        string calldata shopName,
        string calldata licenseNumber,
        string calldata location
    ) external onlyOwner {
        require(shopkeeper != address(0), "Invalid shopkeeper address");
        if (!authorizedShopkeepers[shopkeeper].isAuthorized) {
            shopkeeperList.push(shopkeeper);
        }
        authorizedShopkeepers[shopkeeper] = Shopkeeper({
            wallet: shopkeeper,
            shopName: shopName,
            licenseNumber: licenseNumber,
            location: location,
            isAuthorized: true
        });
        emit ShopkeeperAuthorized(shopkeeper, shopName, licenseNumber);
    }

    function revokeShopkeeper(address shopkeeper) external onlyOwner {
        require(authorizedShopkeepers[shopkeeper].isAuthorized, "Not an authorized shopkeeper");
        authorizedShopkeepers[shopkeeper].isAuthorized = false;
        emit ShopkeeperRevoked(shopkeeper);
    }

    function getShopkeeperCount() external view returns (uint256) {
        return shopkeeperList.length;
    }

    function isShopkeeperAuthorized(address shopkeeper) external view returns (bool) {
        return authorizedShopkeepers[shopkeeper].isAuthorized;
    }

    // 1. Livestock Biometric NFT Minting
    function registerPassport(
        string calldata cowId,
        string calldata biometricHash,
        string calldata ipfsPassportCid,
        string calldata animalName,
        string calldata breed,
        string calldata farmName,
        address initialOwner
    ) external returns (uint256) {
        require(bytes(cowId).length > 0, "Invalid cowId");
        require(cowIdToTokenId[cowId] == 0, "Biometric Passport already registered");

        totalSupply++;
        uint256 tokenId = totalSupply;
        address recipient = initialOwner != address(0) ? initialOwner : msg.sender;

        _owners[tokenId] = recipient;
        _balances[recipient]++;
        cowIdToTokenId[cowId] = tokenId;

        passports[tokenId] = LivestockPassport({
            tokenId: tokenId,
            cowId: cowId,
            biometricHash: biometricHash,
            ipfsPassportCid: ipfsPassportCid,
            animalName: animalName,
            breed: breed,
            farmName: farmName,
            currentOwner: recipient,
            status: AnimalStatus.ALIVE_REGISTERED,
            currentCondition: "HEALTHY",
            registrationDate: block.timestamp
        });

        _provenanceHistory[tokenId].push(ProvenanceRecord({
            tokenId: tokenId,
            from: address(0),
            to: recipient,
            timestamp: block.timestamp,
            condition: "Initial Biometric Registration - Pristine Health",
            transferPurpose: "INITIAL_REGISTRATION",
            certificateId: "MINT"
        }));

        emit Transfer(address(0), recipient, tokenId);
        emit PassportMinted(tokenId, cowId, recipient, biometricHash);
        return tokenId;
    }

    // 2. Peer-to-Peer Ownership Transfer with Condition
    function transferPassportWithCondition(
        uint256 tokenId,
        address to,
        string calldata condition,
        string calldata certificateId
    ) external {
        address from = ownerOf(tokenId);
        require(msg.sender == from || msg.sender == contractOwner, "Unauthorized: Not animal owner");
        require(to != address(0), "Cannot transfer to zero address");

        _balances[from]--;
        _balances[to]++;
        _owners[tokenId] = to;

        passports[tokenId].currentOwner = to;
        passports[tokenId].currentCondition = condition;

        _provenanceHistory[tokenId].push(ProvenanceRecord({
            tokenId: tokenId,
            from: from,
            to: to,
            timestamp: block.timestamp,
            condition: condition,
            transferPurpose: "OWNERSHIP_TRANSFER",
            certificateId: certificateId
        }));

        emit Transfer(from, to, tokenId);
        emit OwnershipTransferredWithCondition(tokenId, from, to, condition, certificateId);
    }

    // 3. Batch Custody Transfer to Slaughterhouse
    function transferToSlaughterhouse(
        uint256[] calldata tokenIds,
        address slaughterhouse,
        string calldata batchId,
        string calldata transitCondition
    ) external {
        require(authorizedSlaughterhouses[slaughterhouse].isAuthorized, "Destination is not an authorized slaughterhouse");
        require(tokenIds.length > 0, "Empty cattle batch");

        for (uint256 i = 0; i < tokenIds.length; i++) {
            uint256 tokenId = tokenIds[i];
            address from = ownerOf(tokenId);
            require(msg.sender == from || msg.sender == contractOwner, "Unauthorized transfer of cow in batch");

            _balances[from]--;
            _balances[slaughterhouse]++;
            _owners[tokenId] = slaughterhouse;

            passports[tokenId].currentOwner = slaughterhouse;
            passports[tokenId].status = AnimalStatus.RECEIVED_AT_SLAUGHTERHOUSE;
            passports[tokenId].currentCondition = transitCondition;

            _provenanceHistory[tokenId].push(ProvenanceRecord({
                tokenId: tokenId,
                from: from,
                to: slaughterhouse,
                timestamp: block.timestamp,
                condition: transitCondition,
                transferPurpose: "TRANSIT_TO_SLAUGHTERHOUSE",
                certificateId: batchId
            }));

            emit Transfer(from, slaughterhouse, tokenId);
            emit CustodyTransferredToSlaughterhouse(tokenId, passports[tokenId].cowId, slaughterhouse, batchId);
        }
    }

    // 4. Halal Slaughter Digital Signature
    function signHalalSlaughter(
        uint256[] calldata tokenIds,
        string calldata halalCertNumber,
        string calldata
    ) external onlyAuthorizedSlaughterhouse {
        require(tokenIds.length > 0, "No cattle specified");

        for (uint256 i = 0; i < tokenIds.length; i++) {
            uint256 tokenId = tokenIds[i];
            require(passports[tokenId].status == AnimalStatus.RECEIVED_AT_SLAUGHTERHOUSE, "Cow not in slaughterhouse custody");

            passports[tokenId].status = AnimalStatus.SLAUGHTERED_HALAL;
            passports[tokenId].currentCondition = "Halal Slaughtered (100% Zibah Verified)";

            _provenanceHistory[tokenId].push(ProvenanceRecord({
                tokenId: tokenId,
                from: msg.sender,
                to: msg.sender,
                timestamp: block.timestamp,
                condition: "Halal Slaughter Complete (100% Zibah Verified)",
                transferPurpose: "HALAL_SLAUGHTER_VERIFIED",
                certificateId: halalCertNumber
            }));

            emit HalalSlaughterSigned(tokenId, passports[tokenId].cowId, msg.sender, block.timestamp, halalCertNumber);
        }
    }

    // 5. Child Meat Packages Creation
    function generateMeatPackages(
        uint256 parentTokenId,
        string[] calldata cutTypes,
        uint256[] calldata weightGramsList,
        string calldata batchId,
        address transporterOrRecipient
    ) external onlyAuthorizedSlaughterhouse returns (uint256[] memory) {
        require(passports[parentTokenId].status == AnimalStatus.SLAUGHTERED_HALAL, "Animal not halal slaughtered yet");
        require(cutTypes.length == weightGramsList.length, "Mismatch in cuts and weights");

        uint256 count = cutTypes.length;
        uint256[] memory createdIds = new uint256[](count);
        address holder = transporterOrRecipient != address(0) ? transporterOrRecipient : msg.sender;
        string memory pCow = passports[parentTokenId].cowId;

        for (uint256 i = 0; i < count; i++) {
            totalPackages++;
            uint256 pkgId = totalPackages;
            string memory pkgTag = string(abi.encodePacked("PKG-", pCow, "-", cutTypes[i]));

            MeatPackage storage mp = meatPackages[pkgId];
            mp.packageId = pkgId;
            mp.packageTag = pkgTag;
            mp.parentTokenId = parentTokenId;
            mp.parentCowId = pCow;
            mp.cutType = cutTypes[i];
            mp.weightGrams = weightGramsList[i];
            mp.batchId = batchId;
            mp.currentHolder = holder;

            packageTagToPackageId[pkgTag] = pkgId;
            _parentToPackageIds[parentTokenId].push(pkgId);
            createdIds[i] = pkgId;

            emit MeatPackageCreated(pkgId, pkgTag, parentTokenId, cutTypes[i], weightGramsList[i]);
        }
        return createdIds;
    }

    // 6. Supermarket / Retailer Delivery Confirmation
    function confirmRetailDelivery(
        uint256[] calldata packageIds,
        string calldata shopName,
        string calldata
    ) external onlyAuthorizedShopkeeper {
        require(packageIds.length > 0, "No packages provided");

        for (uint256 i = 0; i < packageIds.length; i++) {
            uint256 pId = packageIds[i];
            require(meatPackages[pId].packageId > 0, "Package does not exist");
            require(!meatPackages[pId].isDeliveredToRetail, "Package already marked received");

            meatPackages[pId].retailShopName = shopName;
            meatPackages[pId].currentHolder = msg.sender;
            meatPackages[pId].isDeliveredToRetail = true;

            emit RetailDeliveryConfirmed(pId, meatPackages[pId].packageTag, msg.sender, shopName, block.timestamp);
        }
    }

    function supportsInterface(bytes4 interfaceId) external pure returns (bool) {
        return interfaceId == 0x80ac58cd // ERC721
            || interfaceId == 0x5b5e139f // ERC721Metadata
            || interfaceId == 0x01ffc9a7; // ERC165
    }

    function tokenURI(uint256 tokenId) public view returns (string memory) {
        require(_owners[tokenId] != address(0), "Token does not exist");
        string memory cid = passports[tokenId].ipfsPassportCid;
        if (bytes(cid).length == 0) {
            return "";
        }
        return string(abi.encodePacked("https://ipfs.io/ipfs/", cid));
    }

    // View Functions
    function getPassport(uint256 tokenId) external view returns (LivestockPassport memory) {
        require(_owners[tokenId] != address(0), "Passport does not exist");
        return passports[tokenId];
    }

    function getPassportByCowId(string calldata cowId) external view returns (LivestockPassport memory) {
        uint256 tId = cowIdToTokenId[cowId];
        require(tId != 0, "Cow not found");
        return passports[tId];
    }

    function getProvenanceHistory(uint256 tokenId) external view returns (ProvenanceRecord[] memory) {
        return _provenanceHistory[tokenId];
    }

    function getMeatPackage(uint256 packageId) external view returns (MeatPackage memory) {
        require(meatPackages[packageId].packageId > 0, "Package not found");
        return meatPackages[packageId];
    }

    function getPackagesByParent(uint256 parentTokenId) external view returns (uint256[] memory) {
        return _parentToPackageIds[parentTokenId];
    }
}
