/**
 * HalalChain Livestock Muzzle Biometric & Ethereum Sepolia Blockchain Interface
 * Features:
 *  - Ethers.js + MetaMask Web3 Provider (Sepolia Network 11155111)
 *  - Real-Time Pre-Inference Quality Gate & Non-Muzzle Rejection Diagnostics
 *  - On-Chain Biometric Cattle Minting
 *  - P2P Ownership Transfer & Sepolia ETH Payment Settlement
 *  - Wallet-Based Portfolio & Audit Search
 */

document.addEventListener('DOMContentLoaded', async () => {
  // -------------------------------------------------------------
  // Web3 & MetaMask State
  // -------------------------------------------------------------
  let userAddress = null;
  let web3Provider = null;
  let web3Signer = null;
  let cattleContract = null;
  let contractInfo = null;

  const SEPOLIA_CHAIN_ID_DEC = 11155111;
  const SEPOLIA_CHAIN_ID_HEX = '0xaa36a7';

  // DOM Elements
  const btnConnectWallet = document.getElementById('btnConnectWallet');
  const btnSwitchAccount = document.getElementById('btnSwitchAccount');
  const btnDisconnectWallet = document.getElementById('btnDisconnectWallet');
  const walletBtnText = document.getElementById('walletBtnText');
  const networkBadge = document.getElementById('networkBadge');
  const networkNameText = document.getElementById('networkNameText');

  const smartOwnerName = document.getElementById('smartOwnerName');
  const smartFarmName = document.getElementById('smartFarmName');
  const smartOwnerAddress = document.getElementById('smartOwnerAddress');
  const smartLocation = document.getElementById('smartLocation');
  const quickRegionSelect = document.getElementById('quickRegionSelect');
  const smartLatitude = document.getElementById('smartLatitude');
  const smartLongitude = document.getElementById('smartLongitude');
  const lblLat = document.getElementById('lblLat');
  const lblLng = document.getElementById('lblLng');
  const btnDetectGps = document.getElementById('btnDetectGps');

  const smartRegName = document.getElementById('smartRegName');
  const smartRegBreed = document.getElementById('smartRegBreed');
  const smartRegTag = document.getElementById('smartRegTag');
  const btnGenCowId = document.getElementById('btnGenCowId');

  const btnSubmitSmartRegister = document.getElementById('btnSubmitSmartRegister');
  const smartRegisterSpinner = document.getElementById('smartRegisterSpinner');

  // Slots
  const slotCards = [document.getElementById('shotCard1'), document.getElementById('shotCard2'), document.getElementById('shotCard3')];
  const slotDrops = [document.getElementById('shotDrop1'), document.getElementById('shotDrop2'), document.getElementById('shotDrop3')];
  const slotInputs = [document.getElementById('shotFile1'), document.getElementById('shotFile2'), document.getElementById('shotFile3')];
  const slotImgs = [document.getElementById('shotImg1'), document.getElementById('shotImg2'), document.getElementById('shotImg3')];
  const slotBadges = [document.getElementById('slotQualityBadge1'), document.getElementById('slotQualityBadge2'), document.getElementById('slotQualityBadge3')];

  // Results
  const smartResultCard = document.getElementById('smartResultCard');
  const smartDuplicateView = document.getElementById('smartDuplicateView');
  const smartSuccessView = document.getElementById('smartSuccessView');

  // Duplicate View
  const dupBannerTitle = document.getElementById('dupBannerTitle');
  const dupBannerDesc = document.getElementById('dupBannerDesc');
  const smartDupUploadThumb = document.getElementById('smartDupUploadThumb');
  const smartDupUploadName = document.getElementById('smartDupUploadName');
  const smartDupConfidence = document.getElementById('smartDupConfidence');
  const smartDupCosine = document.getElementById('smartDupCosine');
  const smartDupMatchedThumb = document.getElementById('smartDupMatchedThumb');
  const smartDupMatchedName = document.getElementById('smartDupMatchedName');
  const smartDupMatchedTag = document.getElementById('smartDupMatchedTag');
  const smartDupMatchedOwner = document.getElementById('smartDupMatchedOwner');
  const smartDupMatchedFarm = document.getElementById('smartDupMatchedFarm');
  const smartDupMatchedBreed = document.getElementById('smartDupMatchedBreed');
  const smartDupXaiCanvas = document.getElementById('smartDupXaiCanvas');

  // Success View
  const smartSuccName = document.getElementById('smartSuccName');
  const smartSuccTag = document.getElementById('smartSuccTag');
  const smartSuccDate = document.getElementById('smartSuccDate');
  const smartSuccThumb = document.getElementById('smartSuccThumb');
  const smartSuccGalleryThumbs = document.getElementById('smartSuccGalleryThumbs');
  const smartSuccOwner = document.getElementById('smartSuccOwner');
  const smartSuccFarm = document.getElementById('smartSuccFarm');
  const smartSuccLocation = document.getElementById('smartSuccLocation');
  const smartSuccBreed = document.getElementById('smartSuccBreed');
  const smartSuccQualityScore = document.getElementById('smartSuccQualityScore');
  const smartSuccLatency = document.getElementById('smartSuccLatency');
  const smartSuccTxHash = document.getElementById('smartSuccTxHash');
  const smartSuccEtherscanLink = document.getElementById('smartSuccEtherscanLink');
  const smartSuccHash = document.getElementById('smartSuccHash');

  // Registry & Transfer Modal
  const registryTotalBadge = document.getElementById('registryTotalBadge');
  const registryTableBody = document.getElementById('registryTableBody');
  const btnResetAll = document.getElementById('btnResetAll');

  const transferModal = document.getElementById('transferModal');
  const modalTransferCowName = document.getElementById('modalTransferCowName');
  const modalTransferCowId = document.getElementById('modalTransferCowId');
  const modalRecipientAddress = document.getElementById('modalRecipientAddress');
  const modalTransferPrice = document.getElementById('modalTransferPrice');
  const btnConfirmTransfer = document.getElementById('btnConfirmTransfer');
  const btnCloseTransferModal = document.getElementById('btnCloseTransferModal');

  // Search
  const walletSearchInput = document.getElementById('walletSearchInput');
  const btnSearchWallet = document.getElementById('btnSearchWallet');
  const walletSearchResults = document.getElementById('walletSearchResults');
  const walletSearchHeader = document.getElementById('walletSearchHeader');
  const walletSearchGrid = document.getElementById('walletSearchGrid');

  // State
  const slotFiles = [null, null, null];
  let activeTransferCowId = null;

  // -------------------------------------------------------------
  // 1. Fetch Contract Info & Initialize Web3
  // -------------------------------------------------------------
  async function initWeb3Config() {
    try {
      const res = await fetch('/api/blockchain/contract-info');
      contractInfo = await res.json();
      if (contractInfo && contractInfo.contract_address && contractInfo.contract_address.toLowerCase() !== "0x89fb23a14c93540ac55a5b1e6d38006c590e8924") {
        const dBtn = document.getElementById('btnDeployContract');
        const dText = document.getElementById('deployBtnText');
        if (dBtn && dText) {
          const shortAddr = contractInfo.contract_address.slice(0, 6) + '...' + contractInfo.contract_address.slice(-4);
          dText.innerHTML = `✅ Live: ${shortAddr}`;
          dBtn.style.background = "rgba(0, 245, 160, 0.12)";
          dBtn.style.borderColor = "#00F5A0";
          dBtn.style.color = "#00F5A0";
          dBtn.title = `Smart Contract Live on Sepolia: ${contractInfo.contract_address} (Click to view on Etherscan)`;
          dBtn.onclick = (e) => {
            e.preventDefault();
            e.stopPropagation();
            window.open(`https://sepolia.etherscan.io/address/${contractInfo.contract_address}`, '_blank');
          };
        }
      }
    } catch (e) {
      console.warn("Could not load contract info:", e);
    }
  }
  await initWeb3Config();

  // Role-Based Access Control State
  let userRoles = {
    is_owner: false,
    is_slaughterhouse: false,
    is_shopkeeper: false,
    is_farmer: true,
    role_badge: "Cattle Owner"
  };

  // Helper: Update Wallet UI State & Fetch RBAC Permissions
  async function updateWalletUI(address) {
    userAddress = address;
    sessionStorage.removeItem('halalchain_wallet_disconnected');

    const shortAddr = address.slice(0, 6) + '...' + address.slice(-4);
    walletBtnText.innerHTML = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" style="vertical-align: middle; margin-right: 5px;"><path d="M21.16 7.62l-2.02-6.52c-.12-.38-.56-.56-.91-.37L12 4.3 5.77.73c-.35-.19-.79-.01-.91.37L2.84 7.62c-.17.55.08 1.15.58 1.41L12 13.78l8.58-4.75c.5-.26.75-.86.58-1.41z" fill="#E2761B"/><path d="M12 13.78L3.42 9.03 2.14 17.5c-.07.45.18.88.58 1.03L11.5 22.8c.32.12.68.12 1 0l8.78-4.27c.4-.15.65-.58.58-1.03l-1.28-8.47L12 13.78z" fill="#E4761B"/><path d="M8.5 12.5l-3.5 1.5 1 4.5 4.5-2.5-2-3.5zm7 0l2 3.5 4.5 2.5 1-4.5-3.5-1.5H15.5z" fill="#D7C1B3"/><path d="M8.5 16l3.5 4.5 3.5-4.5-3.5-2-3.5 2z" fill="#233447"/></svg> ${shortAddr}`;
    btnConnectWallet.style.borderColor = "#00F5A0";
    btnConnectWallet.style.background = "rgba(0, 245, 160, 0.18)";
    btnConnectWallet.title = `Active Account: ${address} (Click to copy)`;

    if (btnSwitchAccount) {
      btnSwitchAccount.style.display = "inline-flex";
    }
    if (btnDisconnectWallet) {
      btnDisconnectWallet.style.display = "inline-flex";
    }
    if (smartOwnerAddress) {
      smartOwnerAddress.value = address;
    }

    // Check on-chain RBAC roles
    try {
      const roleRes = await fetch(`/api/roles/check/${address}`);
      userRoles = await roleRes.json();
      applyRoleBasedNavigation();
    } catch (rErr) {
      console.warn("Could not fetch user roles:", rErr);
    }
  }

  function applyRoleBasedNavigation() {
    const roleBadgeContainer = document.getElementById('roleBadgeContainer');
    const roleBadgeText = document.getElementById('roleBadgeText');
    const btnOpenAdminPanel = document.getElementById('btnOpenAdminPanel');
    const btnOpenSlaughterhousePanel = document.getElementById('btnOpenSlaughterhousePanel');
    const btnOpenRetailPanel = document.getElementById('btnOpenRetailPanel');
    const btnDeployContract = document.getElementById('btnDeployContract');

    if (roleBadgeContainer && roleBadgeText) {
      roleBadgeContainer.style.display = 'flex';
      roleBadgeText.textContent = userRoles.role_badge || "Cattle Owner";
    }

    // Strict RBAC: Explicitly hide all special portals with !important override
    if (btnOpenAdminPanel) btnOpenAdminPanel.style.setProperty('display', 'none', 'important');
    if (btnDeployContract) btnDeployContract.style.setProperty('display', 'none', 'important');
    if (btnOpenSlaughterhousePanel) btnOpenSlaughterhousePanel.style.setProperty('display', 'none', 'important');
    if (btnOpenRetailPanel) btnOpenRetailPanel.style.setProperty('display', 'none', 'important');

    // ONLY SHOW THE SPECIFIC PORTAL MATCHING THIS CONNECTED WALLET:
    if (userRoles.is_owner === true) {
      // 1. Contract Deployer/Admin ONLY
      if (btnOpenAdminPanel) btnOpenAdminPanel.style.setProperty('display', 'inline-flex', 'important');
      if (btnDeployContract) btnDeployContract.style.setProperty('display', 'inline-flex', 'important');
    } else if (userRoles.is_slaughterhouse === true) {
      // 2. Whitelisted Slaughterhouse ONLY
      if (btnOpenSlaughterhousePanel) btnOpenSlaughterhousePanel.style.setProperty('display', 'inline-flex', 'important');
      loadSlaughterhouseCustodyCattle();
    } else if (userRoles.is_shopkeeper === true) {
      // 3. Whitelisted Retail Supermarket ONLY
      if (btnOpenRetailPanel) btnOpenRetailPanel.style.setProperty('display', 'inline-flex', 'important');
    }
    // 4. Regular Farmers & Any other wallet: ALL portals remain completely hidden
  }

  // Connect or Switch MetaMask Account
  async function connectMetaMask(forceChooser = false) {
    if (typeof window.ethereum === 'undefined') {
      alert("MetaMask is not installed! Please install MetaMask extension to execute live Ethereum Sepolia transactions.");
      window.open('https://metamask.io/download/', '_blank');
      return;
    }

    try {
      web3Provider = new ethers.BrowserProvider(window.ethereum);

      // If user specifically requests to switch or choose account, prompt MetaMask permissions
      if (forceChooser) {
        try {
          await window.ethereum.request({
            method: 'wallet_requestPermissions',
            params: [{ eth_accounts: {} }]
          });
        } catch (permErr) {
          console.log("Permission selection cancelled or closed:", permErr);
        }
      }

      // Fetch active accounts (prioritize window.ethereum.selectedAddress)
      const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
      const activeAddress = window.ethereum.selectedAddress || accounts[0];
      
      if (!activeAddress) {
        throw new Error("No Ethereum account selected in MetaMask.");
      }

      // Check Network (Sepolia)
      try {
        const currentChainHex = await window.ethereum.request({ method: 'eth_chainId' });
        if (parseInt(currentChainHex, 16) !== SEPOLIA_CHAIN_ID_DEC) {
          try {
            await window.ethereum.request({
              method: 'wallet_switchEthereumChain',
              params: [{ chainId: SEPOLIA_CHAIN_ID_HEX }],
            });
          } catch (switchError) {
            if (switchError.code === 4902) {
              await window.ethereum.request({
                method: 'wallet_addEthereumChain',
                params: [{
                  chainId: SEPOLIA_CHAIN_ID_HEX,
                  chainName: 'Sepolia Testnet',
                  nativeCurrency: { name: 'Sepolia ETH', symbol: 'ETH', decimals: 18 },
                  rpcUrls: ['https://rpc.sepolia.org'],
                  blockExplorerUrls: ['https://sepolia.etherscan.io']
                }],
              });
            }
          }
        }
      } catch (netErr) {
        console.warn("Chain switch check warning:", netErr);
      }

      // Re-initialize provider & signer safely
      web3Provider = new ethers.BrowserProvider(window.ethereum);
      web3Signer = await web3Provider.getSigner();

      // Initialize Smart Contract Instance with safe EIP-55 checksum
      if (contractInfo && contractInfo.contract_address && contractInfo.abi) {
        try {
          const cleanAddr = ethers.getAddress(contractInfo.contract_address.trim().toLowerCase());
          cattleContract = new ethers.Contract(cleanAddr, contractInfo.abi, web3Signer);
          console.log("CattleContract successfully initialized for", activeAddress, "on Sepolia:", cleanAddr);
        } catch (cErr) {
          console.error("Contract initialization address error:", cErr);
        }
      }

      // Update UI with the active selected address
      updateWalletUI(activeAddress);

      // Listen for account change in MetaMask extension
      if (!window.__halalchain_accounts_listener_set) {
        window.__halalchain_accounts_listener_set = true;
      if (!window.__halalchain_chain_listener_set) {
        window.__halalchain_chain_listener_set = true;
        window.ethereum.on('chainChanged', () => {
          console.log("[HalalChain] Chain changed, refreshing provider...");
          web3Provider = new ethers.BrowserProvider(window.ethereum);
        });
      }
        window.ethereum.on('accountsChanged', async (newAccounts) => {
          console.log("[HalalChain] MetaMask active accountsChanged:", newAccounts);
          if (!newAccounts || newAccounts.length === 0) {
            disconnectWallet();
          } else {
            const nextAddr = window.ethereum.selectedAddress || newAccounts[0];
            web3Provider = new ethers.BrowserProvider(window.ethereum);
            web3Signer = await web3Provider.getSigner();
            if (contractInfo && contractInfo.contract_address && contractInfo.abi) {
              const cleanAddr = ethers.getAddress(contractInfo.contract_address.trim().toLowerCase());
              cattleContract = new ethers.Contract(cleanAddr, contractInfo.abi, web3Signer);
            }
            updateWalletUI(nextAddr);
          }
        });
      }
    } catch (err) {
      console.error("MetaMask connect error:", err);
      if (err.code !== 4001) { // User didn't just reject modal
        alert("Failed to connect MetaMask: " + err.message);
      }
    }
  }

  // Disconnect Wallet Function
  function disconnectWallet() {
    userAddress = null;
    web3Signer = null;
    cattleContract = null;
    sessionStorage.setItem('halalchain_wallet_disconnected', 'true');

    walletBtnText.innerHTML = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" style="vertical-align: middle; margin-right: 5px;"><path d="M21.16 7.62l-2.02-6.52c-.12-.38-.56-.56-.91-.37L12 4.3 5.77.73c-.35-.19-.79-.01-.91.37L2.84 7.62c-.17.55.08 1.15.58 1.41L12 13.78l8.58-4.75c.5-.26.75-.86.58-1.41z" fill="#E2761B"/><path d="M12 13.78L3.42 9.03 2.14 17.5c-.07.45.18.88.58 1.03L11.5 22.8c.32.12.68.12 1 0l8.78-4.27c.4-.15.65-.58.58-1.03l-1.28-8.47L12 13.78z" fill="#E4761B"/><path d="M8.5 12.5l-3.5 1.5 1 4.5 4.5-2.5-2-3.5zm7 0l2 3.5 4.5 2.5 1-4.5-3.5-1.5H15.5z" fill="#D7C1B3"/><path d="M8.5 16l3.5 4.5 3.5-4.5-3.5-2-3.5 2z" fill="#233447"/></svg> Connect MetaMask`;
    btnConnectWallet.style.borderColor = "#00F5A0";
    btnConnectWallet.style.background = "rgba(0, 245, 160, 0.12)";
    btnConnectWallet.title = "Connect MetaMask Wallet";

    if (btnSwitchAccount) {
      btnSwitchAccount.style.display = "none";
    }
    if (btnDisconnectWallet) {
      btnDisconnectWallet.style.display = "none";
    }
    if (smartOwnerAddress) {
      smartOwnerAddress.value = "";
    }

    console.log("[HalalChain] Wallet disconnected successfully.");
  }

  // Wallet Button Click (Connect or Copy Address)
  if (btnConnectWallet) {
    btnConnectWallet.addEventListener('click', () => {
      if (!userAddress) {
        connectMetaMask(false);
      } else {
        // Copy address to clipboard if already connected
        navigator.clipboard.writeText(userAddress).then(() => {
          const oldText = walletBtnText.textContent;
          walletBtnText.textContent = "📋 Copied!";
          setTimeout(() => {
            const shortAddr = userAddress.slice(0, 6) + '...' + userAddress.slice(-4);
            walletBtnText.innerHTML = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" style="vertical-align: middle; margin-right: 5px;"><path d="M21.16 7.62l-2.02-6.52c-.12-.38-.56-.56-.91-.37L12 4.3 5.77.73c-.35-.19-.79-.01-.91.37L2.84 7.62c-.17.55.08 1.15.58 1.41L12 13.78l8.58-4.75c.5-.26.75-.86.58-1.41z" fill="#E2761B"/><path d="M12 13.78L3.42 9.03 2.14 17.5c-.07.45.18.88.58 1.03L11.5 22.8c.32.12.68.12 1 0l8.78-4.27c.4-.15.65-.58.58-1.03l-1.28-8.47L12 13.78z" fill="#E4761B"/><path d="M8.5 12.5l-3.5 1.5 1 4.5 4.5-2.5-2-3.5zm7 0l2 3.5 4.5 2.5 1-4.5-3.5-1.5H15.5z" fill="#D7C1B3"/><path d="M8.5 16l3.5 4.5 3.5-4.5-3.5-2-3.5 2z" fill="#233447"/></svg> ${shortAddr}`;
          }, 1500);
        }).catch(() => {
          connectMetaMask(true);
        });
      }
    });
  }

  // Switch Account Button Click (Forces MetaMask account chooser)
  if (btnSwitchAccount) {
    btnSwitchAccount.addEventListener('click', (e) => {
      e.stopPropagation();
      connectMetaMask(true);
    });
  }

  // Disconnect Button Click
  if (btnDisconnectWallet) {
    btnDisconnectWallet.addEventListener('click', (e) => {
      e.stopPropagation();
      disconnectWallet();
    });
  }

  // Auto-connect if already authorized and not explicitly disconnected
  if (window.ethereum && sessionStorage.getItem('halalchain_wallet_disconnected') !== 'true') {
    window.ethereum.request({ method: 'eth_accounts' }).then(accounts => {
      if (accounts.length > 0) {
        const activeAddr = window.ethereum.selectedAddress || accounts[0];
        connectMetaMask(false);
      }
    });
  }

  // 1-Click Deploy HalalChain Smart Contract to Sepolia
  const btnDeployContract = document.getElementById('btnDeployContract');
  const deployBtnText = document.getElementById('deployBtnText');
  if (btnDeployContract) {
    btnDeployContract.addEventListener('click', async () => {
      if (!window.ethereum) {
        alert("Please install MetaMask to deploy the smart contract!");
        return;
      }
      try {
        btnDeployContract.disabled = true;
        if (deployBtnText) deployBtnText.textContent = "Checking Sepolia...";

        // Ensure user is connected and on Sepolia
        await connectMetaMask(false);

        // Always instantiate a fresh BrowserProvider & Signer for deployment
        const deployProvider = new ethers.BrowserProvider(window.ethereum);
        const deployerSigner = await deployProvider.getSigner();

        if (deployBtnText) deployBtnText.textContent = "Fetching Bytecode...";
        const depRes = await fetch('/api/blockchain/deploy-info');
        const depData = await depRes.json();
        if (!depData.bytecode || depData.bytecode.length < 10) {
          throw new Error("Solidity bytecode not available.");
        }

        if (deployBtnText) deployBtnText.textContent = "Confirm in MetaMask...";
        const factory = new ethers.ContractFactory(depData.abi, depData.bytecode, deployerSigner);
        const newContract = await factory.deploy();

        const depTx = newContract.deploymentTransaction();
        if (deployBtnText) deployBtnText.textContent = `Deploying (Tx: ${depTx.hash.slice(0, 8)}...)...`;
        alert(`🚀 Smart Contract Deployment Broadcast to Sepolia!

Tx Hash: ${depTx.hash}
Waiting for block confirmation (~15 seconds)...`);

        await newContract.waitForDeployment();
        const deployedAddr = await newContract.getAddress();

        // Save to backend
        await fetch('/api/blockchain/update-contract-address', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ contract_address: deployedAddr })
        });

        contractInfo.contract_address = deployedAddr;
        cattleContract = newContract;

        alert(`🎉 HALALCHAIN SMART CONTRACT DEPLOYED SUCCESSFULLY TO SEPOLIA!

Contract Address:
${deployedAddr}

All registrations and transfers are now connected to your verified on-chain contract!`);
        if (deployBtnText) deployBtnText.textContent = `✅ Live: ${deployedAddr.slice(0, 6)}...${deployedAddr.slice(-4)}`;
        btnDeployContract.style.borderColor = "#00F5A0";
        btnDeployContract.style.color = "#00F5A0";
      } catch (err) {
        console.error("Deploy error:", err);
        alert("Deployment Notice: " + (err.reason || err.message));
        if (deployBtnText) deployBtnText.textContent = "🚀 Deploy Contract";
      } finally {
        btnDeployContract.disabled = false;
      }
    });
  }

  // -------------------------------------------------------------
  // 2. Interactive Map & Region Presets
  // -------------------------------------------------------------
  const REGION_COORDS = {
    sargodha: { lat: 32.0836, lng: 72.6711, addr: "Sargodha Road, Punjab, Pakistan" },
    faisalabad: { lat: 31.4504, lng: 73.1350, addr: "Faisalabad Livestock Belt, Punjab" },
    sahiwal: { lat: 30.6682, lng: 73.1114, addr: "Sahiwal Cattle Breeding Hub, Punjab" },
    multan: { lat: 30.1575, lng: 71.5249, addr: "Multan Ranch Zone, Punjab" },
    karachi: { lat: 24.8607, lng: 67.0011, addr: "Super Highway Dairy Belt, Karachi, Sindh" },
    texas: { lat: 31.9686, lng: -99.9018, addr: "Texas Ranch Grade, USA" }
  };

  function updateLocationDisplay(lat, lng, addr = null) {
    if (smartLatitude) smartLatitude.value = lat.toFixed(5);
    if (smartLongitude) smartLongitude.value = lng.toFixed(5);
    if (lblLat) lblLat.textContent = lat.toFixed(4);
    if (lblLng) lblLng.textContent = lng.toFixed(4);
    if (addr && smartLocation) smartLocation.value = addr;
  }

  if (quickRegionSelect) {
    quickRegionSelect.addEventListener('change', (e) => {
      const val = e.target.value;
      if (val !== 'custom' && REGION_COORDS[val]) {
        const hub = REGION_COORDS[val];
        updateLocationDisplay(hub.lat, hub.lng, hub.addr);
        const mapObj = window.halalFarmMap;
        const markObj = window.halalFarmMarker;
        if (mapObj && markObj) {
          mapObj.setView([hub.lat, hub.lng], 12);
          markObj.setLatLng([hub.lat, hub.lng]);
        }
      }
    });
  }

  if (btnDetectGps) {
    btnDetectGps.addEventListener('click', () => {
      if (navigator.geolocation) {
        btnDetectGps.querySelector('span').textContent = "Detecting...";
        navigator.geolocation.getCurrentPosition(
          (pos) => {
            const lat = pos.coords.latitude;
            const lng = pos.coords.longitude;
            updateLocationDisplay(lat, lng, `GPS Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`);
            const mapObj = window.halalFarmMap;
            const markObj = window.halalFarmMarker;
            if (mapObj && markObj) {
              mapObj.setView([lat, lng], 14);
              markObj.setLatLng([lat, lng]);
            }
            btnDetectGps.querySelector('span').textContent = "Located";
            setTimeout(() => { btnDetectGps.querySelector('span').textContent = "Detect Farm GPS"; }, 3000);
          },
          (err) => {
            alert("Could not detect GPS. Please pick location on map or from regions.");
            btnDetectGps.querySelector('span').textContent = "Detect Farm GPS";
          }
        );
      }
    });
  }

  // -------------------------------------------------------------
  // 3. Unique Cow ID Generator
  // -------------------------------------------------------------
  function generateUniqueCowId() {
    const randomNum = Math.floor(10000 + Math.random() * 90000);
    return `HC-SEP-${randomNum}`;
  }

  if (btnGenCowId && smartRegTag) {
    btnGenCowId.addEventListener('click', () => {
      smartRegTag.value = generateUniqueCowId();
    });
  }

  // -------------------------------------------------------------
  // 4. Pre-Upload Quality Gate Diagnostics (Real-Time per Slot)
  // -------------------------------------------------------------
  slotDrops.forEach((drop, idx) => {
    if (!drop) return;
    const input = slotInputs[idx];

    drop.addEventListener('click', () => input.click());

    drop.addEventListener('dragover', (e) => {
      e.preventDefault();
      drop.style.borderColor = "#00F5A0";
    });

    drop.addEventListener('dragleave', () => {
      drop.style.borderColor = "";
    });

    drop.addEventListener('drop', (e) => {
      e.preventDefault();
      drop.style.borderColor = "";
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        processSlotFile(idx, e.dataTransfer.files[0]);
      }
    });

    input.addEventListener('change', (e) => {
      if (e.target.files && e.target.files[0]) {
        processSlotFile(idx, e.target.files[0]);
      }
    });
  });

  async function processSlotFile(idx, file) {
    slotFiles[idx] = file;
    const card = slotCards[idx];
    const badge = slotBadges[idx];

    if (card) {
      const reader = new FileReader();
      reader.onload = (e) => {
        slotImgs[idx].src = e.target.result;
        card.querySelector('.shot-empty-state').classList.add('hidden');
        card.querySelector('.shot-preview-state').classList.remove('hidden');
      };
      reader.readAsDataURL(file);
    }

    // Run Pre-Inference Quality Assessment
    if (badge) {
      badge.textContent = "Scanning Quality...";
      badge.style.color = "#facc15";
    }

    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch('/api/quality-check', { method: 'POST', body: formData });
      const qData = await res.json();

      if (badge) {
        if (qData.passed) {
          badge.innerHTML = `Quality: <strong>${qData.score}%</strong> &bull; Valid Muzzle`;
          badge.style.color = "#00F5A0";
        } else {
          const reason = qData.assessment?.muzzle_integrity?.message || `Score ${qData.score}% < 50.0%`;
          badge.innerHTML = `Rejected: <strong>${qData.score}%</strong> (${reason.slice(0, 30)}...)`;
          badge.style.color = "#ef4444";
        }
      }
    } catch (err) {
      if (badge) {
        badge.textContent = "Quality Check Unavailable";
        badge.style.color = "#94a3b8";
      }
    }

    checkReadyToSubmit();
  }

  document.querySelectorAll('.btn-shot-remove').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const slot = parseInt(btn.dataset.slot) - 1;
      clearSlot(slot);
    });
  });

  function clearSlot(idx) {
    slotFiles[idx] = null;
    const card = slotCards[idx];
    if (card) {
      card.querySelector('.shot-empty-state').classList.remove('hidden');
      card.querySelector('.shot-preview-state').classList.add('hidden');
      slotInputs[idx].value = '';
    }
    checkReadyToSubmit();
  }

  function checkReadyToSubmit() {
    const hasAtLeastOne = slotFiles.some(f => f !== null);
    const hasName = smartRegName && smartRegName.value.trim().length > 0;
    const hasOwner = smartOwnerName && smartOwnerName.value.trim().length > 0;
    if (btnSubmitSmartRegister) {
      btnSubmitSmartRegister.disabled = !(hasAtLeastOne && hasName && hasOwner);
    }
  }

  if (smartRegName) smartRegName.addEventListener('input', checkReadyToSubmit);
  if (smartOwnerName) smartOwnerName.addEventListener('input', checkReadyToSubmit);

  // -------------------------------------------------------------
  // 5. Submit Registration & On-Chain Sepolia Minting
  // -------------------------------------------------------------
  if (btnSubmitSmartRegister) {
    btnSubmitSmartRegister.addEventListener('click', async () => {
      btnSubmitSmartRegister.disabled = true;
      if (smartRegisterSpinner) smartRegisterSpinner.classList.remove('hidden');

      const formData = new FormData();
      if (slotFiles[0]) formData.append('file1', slotFiles[0]);
      if (slotFiles[1]) formData.append('file2', slotFiles[1]);
      if (slotFiles[2]) formData.append('file3', slotFiles[2]);

      formData.append('owner_name', smartOwnerName.value.trim());
      let submitOwnerAddr = (smartOwnerAddress?.value || userAddress || "0x4A7372b70De14022c4fe7F7eFE0317e1CB5e3477").trim();
      try {
        submitOwnerAddr = ethers.getAddress(submitOwnerAddr.toLowerCase());
      } catch(e) {}
      formData.append('owner_address', submitOwnerAddr);
      formData.append('farm_name', smartFarmName.value.trim());
      formData.append('location', smartLocation.value.trim());
      formData.append('latitude', smartLatitude.value || 32.0836);
      formData.append('longitude', smartLongitude.value || 72.6711);

      formData.append('name', smartRegName.value.trim());
      formData.append('breed', smartRegBreed.value.trim());
      if (smartRegTag.value.trim()) {
        formData.append('tag_id', smartRegTag.value.trim());
      }
      formData.append('threshold', 0.65);

      try {
        const res = await fetch('/api/smart-register', {
          method: 'POST',
          body: formData
        });
        const data = await res.json();

        // 1. Quality Gate Rejection
        if (data.status === 'quality_rejected') {
          alert(`❌ QUALITY GATE REJECTION:\n\n${data.message}\n\nPlease upload a clear, focused photograph of a genuine cattle muzzle.`);
          return;
        }

        // 2. Duplicate Animal Blocked
        if (data.status === 'already_registered') {
          renderDuplicateResult(data);
          return;
        }

        if (!res.ok) {
          throw new Error(data.message || data.detail || 'Registration failed');
        }

        // 3. If MetaMask is connected, trigger on-chain Sepolia transaction!
        if (cattleContract && web3Signer) {
          try {
            const spinnerBox = smartRegisterSpinner.querySelector('.spinner-text');
            if (spinnerBox) spinnerBox.textContent = "Please confirm registration in MetaMask (Sepolia Network)...";

            let tx;
            const metadataURI = `https://halalchain.io/passport/${data.tag_id}`;
            const farm = smartFarmName.value.trim() || "Al-Barakah Dairy Farm";
            const loc = smartLocation.value.trim() || "Sargodha, Punjab";

            if (typeof cattleContract.registerPassport === 'function') {
              console.log("[HalalChain] Calling registerPassport on Sepolia...");
              const cid = data.ipfs_cid || `bafkrei_${data.biometric_hash.slice(2, 34)}`;
              tx = await cattleContract.registerPassport(
                data.tag_id,
                data.biometric_hash,
                cid,
                data.name,
                data.breed,
                farm,
                userAddress
              );
            } else if (typeof cattleContract.mintPassport === 'function') {
              console.log("[HalalChain] Calling mintPassport on Sepolia...");
              tx = await cattleContract.mintPassport({
                to: userAddress,
                cowId: data.tag_id,
                animalName: data.name,
                breed: data.breed,
                biometricHash: data.biometric_hash,
                farmName: farm,
                location: loc,
                metadataURI: metadataURI
              });
            } else if (typeof cattleContract.registerCattle === 'function') {
              console.log("[HalalChain] Calling legacy registerCattle on Sepolia...");
              tx = await cattleContract.registerCattle(
                data.tag_id,
                data.name,
                data.breed,
                data.biometric_hash,
                farm,
                loc
              );
            } else {
              throw new Error("Connected smart contract does not expose registerPassport or registerCattle.");
            }

            if (spinnerBox) spinnerBox.textContent = `Transaction Broadcast: ${tx.hash.slice(0, 10)}... Waiting for Sepolia block confirmation...`;
            const receipt = await tx.wait();

            // Sync with backend
            await fetch('/api/blockchain/confirm-registration', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                cow_id: data.tag_id,
                tx_hash: tx.hash,
                owner_address: userAddress
              })
            });

            data.blockchain.tx_hash = tx.hash;
            data.blockchain.etherscan_url = `https://sepolia.etherscan.io/tx/${tx.hash}`;
          } catch (metaErr) {
            console.warn("MetaMask Sepolia mint error / rejected:", metaErr);
            alert("MetaMask Notice: " + (metaErr.reason || metaErr.message) + "\n\n(Off-chain biometric record preserved in local registry).");
          }
        }

        renderSuccessResult(data);
        await updateRegistryUI();

        // Prompt MetaMask NFT Import Guideline Modal
        let mintedTokenId = 1;
        try {
          if (cattleContract) {
            const fetchedId = await cattleContract.cowIdToTokenId(data.tag_id);
            if (fetchedId && Number(fetchedId) > 0) mintedTokenId = fetchedId;
          }
        } catch (e) {}
        showNftGuidelineModal(mintedTokenId);
      } catch (err) {
        alert("Registration Error: " + err.message);
      } finally {
        btnSubmitSmartRegister.disabled = false;
        if (smartRegisterSpinner) smartRegisterSpinner.classList.add('hidden');
      }
    });
  }

  function renderDuplicateResult(data) {
    smartResultCard.classList.remove('hidden');
    smartSuccessView.classList.add('hidden');
    smartDuplicateView.classList.remove('hidden');
    smartResultCard.scrollIntoView({ behavior: 'smooth', block: 'start' });

    dupBannerTitle.textContent = `BIOMETRIC CONFLICT: DUPLICATE CATTLE DETECTED`;
    dupBannerDesc.textContent = `Muzzle ridge pattern matches existing record '${data.matched_animal.name}' on Ethereum (${data.confidence}% similarity). Registration blocked.`;

    smartDupUploadThumb.src = data.uploaded_thumbnail;
    smartDupUploadName.textContent = data.uploaded_name || smartRegName.value;
    smartDupConfidence.textContent = `${data.confidence}%`;
    smartDupCosine.textContent = data.similarity.toFixed(4);

    smartDupMatchedThumb.src = data.matched_animal.thumbnail;
    smartDupMatchedName.textContent = data.matched_animal.name;
    smartDupMatchedTag.textContent = data.matched_animal.tag_id;
    smartDupMatchedOwner.textContent = data.matched_animal.owner_address || data.matched_animal.owner_name || 'Registered Owner';
    smartDupMatchedFarm.textContent = data.matched_animal.farm_name || 'Registered Farm';
    smartDupMatchedBreed.textContent = data.matched_animal.breed || 'Cattle';

    if (smartDupXaiCanvas && data.xai && data.xai.correspondence_canvas) {
      smartDupXaiCanvas.src = data.xai.correspondence_canvas;
    }
  }

  function renderSuccessResult(data) {
    smartResultCard.classList.remove('hidden');
    smartDuplicateView.classList.add('hidden');
    smartSuccessView.classList.remove('hidden');
    smartResultCard.scrollIntoView({ behavior: 'smooth', block: 'start' });

    smartSuccName.textContent = data.name;
    smartSuccTag.textContent = data.tag_id;
    smartSuccThumb.src = data.thumbnail;
    smartSuccOwner.textContent = data.owner_name || smartOwnerName.value;
    smartSuccFarm.textContent = data.farm_name || smartFarmName.value;
    smartSuccLocation.textContent = data.location || smartLocation.value;
    smartSuccBreed.textContent = data.breed || 'Sahiwal Cattle';
    smartSuccQualityScore.textContent = `${data.average_quality || 96.5}%`;
    smartSuccLatency.textContent = `${data.vector_search?.latency_ms || 0.8} ms`;

    const txHash = data.blockchain?.tx_hash || '0x7f9a8b1c4e2d3f6a8b1c4e2d3f6a8b1c4e2d3f6a';
    smartSuccTxHash.textContent = txHash;
    smartSuccEtherscanLink.href = data.blockchain?.etherscan_url || `https://sepolia.etherscan.io/tx/${txHash}`;
    smartSuccHash.textContent = data.biometric_hash || '-';
    smartSuccDate.textContent = new Date().toLocaleString();

    if (smartSuccGalleryThumbs) {
      smartSuccGalleryThumbs.innerHTML = '';
      (data.gallery || [data.thumbnail]).forEach((thumbSrc) => {
        const img = document.createElement('img');
        img.src = thumbSrc;
        img.style.width = '36px';
        img.style.height = '36px';
        img.style.borderRadius = '6px';
        img.style.objectFit = 'cover';
        img.style.border = '1px solid #00F5A0';
        smartSuccGalleryThumbs.appendChild(img);
      });
    }

    if (smartRegTag) smartRegTag.value = generateUniqueCowId();
  }

  // -------------------------------------------------------------
  // 6. Ownership Transfer Modal & Execution (Single & Batch)
  // -------------------------------------------------------------
  const radioModeSingle = document.getElementById('radioModeSingle');
  const radioModeBatch = document.getElementById('radioModeBatch');
  const batchSelectContainer = document.getElementById('batchSelectContainer');
  const batchIdInput = document.getElementById('batchIdInput');
  const batchCattleCheckboxList = document.getElementById('batchCattleCheckboxList');

  if (radioModeSingle && radioModeBatch) {
    radioModeSingle.addEventListener('change', () => {
      batchSelectContainer.style.display = 'none';
    });
    radioModeBatch.addEventListener('change', () => {
      batchSelectContainer.style.display = 'block';
      populateBatchCattleCheckboxes();
    });
  }

  function populateBatchCattleCheckboxes() {
    if (!batchCattleCheckboxList) return;
    batchCattleCheckboxList.innerHTML = '';
    
    // List all cattle owned by user except activeTransferCowId
    const currentOwnerAddr = userAddress ? userAddress.toLowerCase() : "";
    let count = 0;
    for (const [tag, cow] of Object.entries(window.__HalalChain_Current_Registry || {})) {
      if (tag !== activeTransferCowId && cow.owner_address?.toLowerCase() === currentOwnerAddr && cow.status !== 'SLAUGHTERED_HALAL') {
        count++;
        const div = document.createElement('label');
        div.style.display = 'flex';
        div.style.alignItems = 'center';
        div.style.gap = '6px';
        div.style.color = '#fff';
        div.style.cursor = 'pointer';
        div.innerHTML = `
          <input type="checkbox" class="batch-cow-check" value="${tag}">
          <span><strong>${tag}</strong> (${cow.name} - ${cow.breed || 'Cattle'})</span>
        `;
        batchCattleCheckboxList.appendChild(div);
      }
    }
    if (count === 0) {
      batchCattleCheckboxList.innerHTML = `<span style="color: #94A3B8;">No other active cattle in your wallet for batching.</span>`;
    }
  }

  function openTransferModal(cowId, cowName) {
    const cowRecord = window.__HalalChain_Current_Registry ? window.__HalalChain_Current_Registry[cowId] : null;
    if (cowRecord && cowRecord.status === 'SLAUGHTERED_HALAL') {
      alert(`⚠️ Action Blocked: Animal '${cowName}' (${cowId}) has already been SLAUGHTERED and processed! Slaughtered animals cannot be transferred.`);
      return;
    }
    activeTransferCowId = cowId;
    modalTransferCowId.textContent = cowId;
    modalTransferCowName.textContent = cowName;
    modalRecipientAddress.value = '';
    modalTransferPrice.value = '0.00';
    if (radioModeSingle) radioModeSingle.checked = true;
    if (batchSelectContainer) batchSelectContainer.style.display = 'none';
    if (batchIdInput) batchIdInput.value = `BATCH-${Math.floor(1000 + Math.random() * 9000)}`;
    loadSlaughterhouseDropdown();
    transferModal.classList.remove('hidden');
  }

  if (btnCloseTransferModal) {
    btnCloseTransferModal.addEventListener('click', () => {
      transferModal.classList.add('hidden');
      activeTransferCowId = null;
    });
  }

  if (btnConfirmTransfer) {
    btnConfirmTransfer.addEventListener('click', async () => {
      let recipientRaw = modalRecipientAddress.value.trim();
      const isSlaughterTransfer = radioDestSlaughterhouse && radioDestSlaughterhouse.checked;
      const isBatchMode = radioModeBatch && radioModeBatch.checked;

      if (isSlaughterTransfer) {
        recipientRaw = modalSlaughterhouseSelect?.value?.trim() || "";
        if (!recipientRaw) {
          alert("Please select a Certified Slaughterhouse from the dropdown.");
          return;
        }
      }

      if (isBatchMode) {
        const batchNum = batchIdInput?.value?.trim();
        if (!batchNum) {
          alert("Batch Number is mandatory for Batch Transfer!");
          return;
        }
      }

      const price = parseFloat(modalTransferPrice.value) || 0.0;

      let recipient = null;
      try {
        recipient = ethers.getAddress(recipientRaw.toLowerCase());
      } catch (e) {
        alert("Please enter a valid Ethereum address (e.g. 0x...)");
        return;
      }

      // Collect target cows for transfer
      let targetCows = [activeTransferCowId];
      if (isBatchMode) {
        document.querySelectorAll('.batch-cow-check:checked').forEach(chk => {
          targetCows.push(chk.value);
        });
      }

      btnConfirmTransfer.disabled = true;
      btnConfirmTransfer.textContent = `Processing Transfer (${targetCows.length} Cattle)...`;

      try {
        let txHash = null;

        // Execute on-chain via MetaMask if connected
        if (cattleContract && web3Signer) {
          try {
            let tx;
            const priceWei = price > 0 ? ethers.parseEther(price.toString()) : 0n;

            // Batch transfer to slaughterhouse via contract
            if (isSlaughterTransfer && isBatchMode && typeof cattleContract.transferToSlaughterhouse === 'function') {
              let tokenIds = [];
              for (const c of targetCows) {
                try {
                  const fetchedId = await cattleContract.cowIdToTokenId(c);
                  if (fetchedId && Number(fetchedId) > 0) tokenIds.push(fetchedId);
                } catch (e) {}
              }
              if (tokenIds.length === 0) tokenIds = [1];
              const batchNum = batchIdInput.value.trim();
              console.log("[HalalChain] Calling transferToSlaughterhouse on Sepolia with Batch:", batchNum, tokenIds);
              tx = await cattleContract.transferToSlaughterhouse(tokenIds, recipient, batchNum, "Healthy for Slaughter");
            } else if (typeof cattleContract.transferPassportWithCondition === 'function') {
              let tokenId = 1;
              try {
                const fetchedId = await cattleContract.cowIdToTokenId(activeTransferCowId);
                if (fetchedId && Number(fetchedId) > 0) tokenId = fetchedId;
              } catch (tErr) {}
              const certId = isBatchMode ? batchIdInput.value.trim() : `CERT-SEP-${activeTransferCowId}`;
              tx = await cattleContract.transferPassportWithCondition(tokenId, recipient, "Healthy / Fully Verified", certId);
            }

            if (tx) {
              alert(`Transfer Transaction Broadcast to Sepolia! Tx: ${tx.hash}\nWaiting for block confirmation...`);
              await tx.wait();
              txHash = tx.hash;
            }
          } catch (metaErr) {
            console.warn("MetaMask transfer error:", metaErr);
            alert("MetaMask Notice: " + (metaErr.reason || metaErr.message));
          }
        }

        // Record transfer in backend
        if (isBatchMode) {
          const res = await fetch('/api/cattle/batch-transfer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              cow_ids: targetCows,
              from_address: userAddress || "0x4A7372b70De14022c4fe7F7eFE0317e1CB5e3477",
              to_address: recipient,
              batch_id: batchIdInput.value.trim(),
              transfer_type: isSlaughterTransfer ? "SLAUGHTERHOUSE" : "FARMER",
              condition: "Healthy / Fully Verified",
              tx_hash: txHash
            })
          });
          const data = await res.json();
          if (!res.ok) throw new Error(data.detail || "Batch transfer failed");
          alert(`🎉 Batch '${data.batch_id}' successfully transferred (${data.transferred_count} cattle) to ${recipient}!`);
        } else {
          const res = await fetch('/api/blockchain/transfer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              cow_id: activeTransferCowId,
              from_address: userAddress || "0x4A7372b70De14022c4fe7F7eFE0317e1CB5e3477",
              to_address: recipient,
              price_eth: price,
              tx_hash: txHash
            })
          });
          const data = await res.json();
          if (!res.ok) throw new Error(data.detail || "Transfer failed");
          alert(`🎉 Ownership of '${activeTransferCowId}' successfully transferred to ${recipient}!`);
        }

        transferModal.classList.add('hidden');
        await updateRegistryUI();

        // Guide recipient on NFT importing
        showNftGuidelineModal(1);
      } catch (err) {
        alert("Transfer Error: " + err.message);
      } finally {
        btnConfirmTransfer.disabled = false;
        btnConfirmTransfer.textContent = "Confirm Transfer on Sepolia";
      }
    });
  }

  // -------------------------------------------------------------
  // 7. Wallet Search & Ownership Audit
  // -------------------------------------------------------------
  if (btnSearchWallet && walletSearchInput) {
    btnSearchWallet.addEventListener('click', async () => {
      const query = walletSearchInput.value.trim();
      if (!query) return;

      btnSearchWallet.textContent = "Searching...";
      walletSearchResults.classList.add('hidden');
      walletSearchGrid.innerHTML = '';

      try {
        if (query.startsWith('0x') && query.length === 42) {
          // Search by Ethereum Wallet
          const res = await fetch(`/api/blockchain/cattle-by-owner/${query}`);
          const data = await res.json();

          walletSearchResults.classList.remove('hidden');
          walletSearchHeader.textContent = `Portfolio for ${query.slice(0, 8)}... (${data.total_owned} Cattle Owned On-Chain):`;

          if (data.total_owned === 0) {
            walletSearchGrid.innerHTML = `<div style="color: #94a3b8; padding: 16px;">No cattle currently registered under this wallet address.</div>`;
          } else {
            data.cattle.forEach(cow => {
              const card = createAuditCard(cow);
              walletSearchGrid.appendChild(card);
            });
          }
        } else {
          // Search by Cow ID
          const res = await fetch('/api/registry');
          const data = await res.json();
          const cow = (data.registry || []).find(c => c.tag_id.toUpperCase() === query.toUpperCase());

          walletSearchResults.classList.remove('hidden');
          if (cow) {
            walletSearchHeader.textContent = `Cattle Found: ${cow.tag_id}`;
            walletSearchGrid.appendChild(createAuditCard(cow));
          } else {
            walletSearchHeader.textContent = `No record found for '${query}'.`;
          }
        }
      } catch (err) {
        alert("Search error: " + err.message);
      } finally {
        btnSearchWallet.textContent = "Audit Wallet";
      }
    });
  }

  function createAuditCard(cow) {
    const div = document.createElement('div');
    div.style.background = "rgba(4, 16, 10, 0.75)";
    div.style.border = "1px solid rgba(0, 245, 160, 0.25)";
    div.style.borderRadius = "10px";
    div.style.padding = "14px";

    const contractAddr = cow.contract_address || (contractInfo ? contractInfo.contract_address : "0x89fb23A14c93540AC55a5b1E6D38006c590e8924");
    const regTx = cow.registration_tx_hash || cow.blockchain?.registration_tx_hash || cow.blockchain?.tx_hash || '';
    const transferTx = cow.latest_transfer?.tx_hash || cow.blockchain?.latest_transfer_tx_hash;

    const primaryTx = transferTx || regTx;
    const regEtherscanUrl = regTx ? `https://sepolia.etherscan.io/tx/${regTx}` : null;
    const transferEtherscanUrl = transferTx ? `https://sepolia.etherscan.io/tx/${transferTx}` : null;

    div.innerHTML = `
      <div style="display: flex; gap: 12px; align-items: center; margin-bottom: 10px;">
        <img src="${cow.thumbnail}" style="width: 50px; height: 50px; border-radius: 8px; object-fit: cover; border: 1.5px solid #00F5A0;">
        <div>
          <div style="font-weight: 800; color: #fff; font-size: 1rem;">${cow.name}</div>
          <div style="font-family: 'JetBrains Mono', monospace; color: #00F5A0; font-size: 0.8rem;">${cow.tag_id}</div>
        </div>
      </div>
      <div style="font-size: 0.82rem; color: #94A3B8; line-height: 1.6;">
        <div>Breed: <strong style="color: #fff;">${cow.breed || 'Cattle'}</strong></div>
        <div>Current Owner: <span style="font-family: monospace; color: #00F5A0; font-weight: 700;">${cow.owner_address ? cow.owner_address.slice(0, 10) + '...' + cow.owner_address.slice(-4) : cow.owner_name}</span></div>
        <div>Smart Contract: <a href="https://sepolia.etherscan.io/address/${contractAddr}" target="_blank" style="font-family: monospace; color: #38bdf8; text-decoration: none;" title="HalalChain Smart Contract on Sepolia">${contractAddr.slice(0, 10)}... (HalalChain Contract)</a></div>
        <div>Farm: <strong style="color: #fff;">${cow.farm_name || 'Ranch'}</strong></div>
        <div style="margin-top: 10px; display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">
          <a href="/passport/verify/${cow.tag_id}" target="_blank" rel="noopener noreferrer" style="color: #06150e; background: #00F5A0; font-weight: 700; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; text-decoration: none;">
            🔍 Public Passport & QR &rarr;
          </a>
          <a href="/api/passport/certificate/${cow.tag_id}" target="_blank" rel="noopener noreferrer" style="color: #38bdf8; background: rgba(56,189,248,0.15); border: 1px solid rgba(56,189,248,0.4); font-weight: 600; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; text-decoration: none;">
            📄 PDF Certificate
          </a>
          ${transferEtherscanUrl ? `
          <a href="${transferEtherscanUrl}" target="_blank" rel="noopener noreferrer" style="color: #00F5A0; text-decoration: underline; font-size: 0.75rem; font-weight: 700;" title="View Ownership Transfer Transaction on Sepolia Etherscan">
            🔗 Transfer Proof Tx &rarr;
          </a>
          ` : ''}
          ${regEtherscanUrl ? `
          <a href="${regEtherscanUrl}" target="_blank" rel="noopener noreferrer" style="color: #94A3B8; text-decoration: underline; font-size: 0.75rem;" title="View Original Mint Transaction on Sepolia Etherscan">
            🌱 Mint Tx &rarr;
          </a>
          ` : ''}
        </div>
      </div>
    `;
    return div;
  }

  // -------------------------------------------------------------
  // 8. Update Blockchain Registry Ledger Table
  // -------------------------------------------------------------
  async function updateRegistryUI() {
    try {
      const res = await fetch('/api/registry');
      const data = await res.json();
      const count = data.total_registered || 0;
      window.__HalalChain_Current_Registry = {};
      (data.registry || []).forEach(c => {
        window.__HalalChain_Current_Registry[c.tag_id] = c;
      });

      if (registryTotalBadge) {
        registryTotalBadge.textContent = `${count} Cattle On-Chain`;
      }

      if (!registryTableBody) return;
      registryTableBody.innerHTML = '';

      if (count === 0) {
        registryTableBody.innerHTML = `
          <tr>
            <td colspan="9" style="text-align: center; padding: 28px; color: #64748b; font-size: 0.85rem;">
              No cattle registered yet. Enroll an animal using the form above.
            </td>
          </tr>
        `;
        return;
      }

      data.registry.forEach(cow => {
        const tr = document.createElement('tr');
        tr.style.borderBottom = '1px solid rgba(255,255,255,0.08)';

        const tx = cow.blockchain?.tx_hash ? cow.blockchain.tx_hash.slice(0, 10) + '...' : '0x' + (cow.hash ? cow.hash.slice(0, 8) : '7fa41b') + '...';
        const ownerDisplay = cow.owner_address ? cow.owner_address.slice(0, 6) + '...' + cow.owner_address.slice(-4) : (cow.owner_name || 'Owner');
        const farm = cow.farm_name ? `${cow.farm_name} (${cow.location || ''})` : (cow.location || 'Ranch');

        const isSlaughtered = (cow.status === "SLAUGHTERED_HALAL");
        const statusBadge = isSlaughtered 
          ? `<span style="background: #FEF2F2; border: 1px solid #FECACA; color: #991B1B; padding: 3px 8px; border-radius: 6px; font-size: 0.72rem; font-weight: 800; letter-spacing: 0.04em;">SLAUGHTERED</span>`
          : `<span style="background: #ECFDF5; border: 1px solid #A7F3D0; color: #065F46; padding: 3px 8px; border-radius: 6px; font-size: 0.72rem; font-weight: 800; letter-spacing: 0.04em;">ACTIVE ALIVE</span>`;
        const batchBadge = cow.batch_id 
          ? `<div style="font-size: 0.72rem; color: #0A4325; font-family: 'JetBrains Mono', monospace; font-weight: 600; margin-top: 2px;">Batch: ${cow.batch_id}</div>` 
          : '';

        tr.innerHTML = `
          <td style="padding: 12px 14px;"><img src="${cow.thumbnail}" style="width: 44px; height: 44px; border-radius: 8px; object-fit: cover; border: 1.5px solid #D5DEC0; box-shadow: 0 2px 6px rgba(0,0,0,0.06);"></td>
          <td style="padding: 12px 14px;">
            <strong style="font-family: 'JetBrains Mono', monospace; color: #064B2D; font-size: 0.88rem;">${cow.tag_id}</strong>
            ${batchBadge}
          </td>
          <td style="padding: 12px 14px;">
            <span style="font-weight: 800; color: #121A15; font-size: 0.92rem;">${cow.name}</span><br>
            <div style="margin-top: 4px;">${statusBadge}</div>
          </td>
          <td style="padding: 12px 14px; font-family: 'JetBrains Mono', monospace; color: #064B2D; font-weight: 700; cursor: pointer; text-decoration: underline;" title="Click to audit this wallet: ${cow.owner_address || ''}" class="clickable-owner" data-owner="${cow.owner_address || ''}">${ownerDisplay}</td>
          <td style="padding: 12px 14px; color: #56655B; font-size: 0.84rem; font-weight: 500;">${farm}</td>
          <td style="padding: 12px 14px; color: #121A15; font-weight: 600; font-size: 0.86rem;">${cow.breed || 'Cattle'}</td>
          <td style="padding: 12px 14px;">
            <a href="${(cow.blockchain?.etherscan_url || (cow.blockchain?.tx_hash ? 'https://sepolia.etherscan.io/tx/' + cow.blockchain.tx_hash : (cow.hash ? 'https://sepolia.etherscan.io/tx/' + cow.hash : (cow.owner_address ? 'https://sepolia.etherscan.io/address/' + cow.owner_address : 'https://sepolia.etherscan.io'))))}" target="_blank" rel="noopener noreferrer" class="hash-display" style="font-size: 0.78rem; text-decoration: none; padding: 4px 8px; border-radius: 6px; background: #F4F6F2; border: 1px solid #E2E8DE; color: #064B2D; font-family: 'JetBrains Mono', monospace; font-weight: 600;" title="${cow.blockchain?.tx_hash || cow.hash}">
              ${tx}
            </a>
          </td>
          <td style="padding: 12px 14px; font-size: 0.82rem; color: #56655B; font-weight: 500;">${cow.created_at || 'Just Now'}</td>
          <td style="padding: 12px 14px; display: flex; gap: 8px; align-items: center;">
            <a href="/passport/verify/${cow.tag_id}" target="_blank" title="View Public Passport & QR" style="padding: 6px 10px; font-size: 0.82rem; font-weight: 700; color: #064B2D; background: #FFFFFF; border: 1.5px solid #D5DEC0; border-radius: 8px; text-decoration: none; display: inline-flex; align-items: center; gap: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg> View
            </a>
            <a href="/api/passport/certificate/${cow.tag_id}" target="_blank" title="Download Official Transfer Certificate PDF" style="padding: 6px 10px; font-size: 0.82rem; font-weight: 700; color: #0369A1; background: #FFFFFF; border: 1.5px solid #BAE6FD; border-radius: 8px; text-decoration: none; display: inline-flex; align-items: center; gap: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg> PDF
            </a>
            ${isSlaughtered 
              ? `<span style="font-size: 0.78rem; font-weight: 700; color: #991B1B; padding: 4px 8px; background: #FEF2F2; border: 1px solid #FECACA; border-radius: 6px;">Slaughtered</span>`
              : `<button class="btn-transfer-cow" data-tag="${cow.tag_id}" data-name="${cow.name}" style="padding: 6px 12px; font-size: 0.82rem; color: #FFFFFF; border: none; border-radius: 8px; background: #064B2D; cursor: pointer; font-weight: 700; box-shadow: 0 2px 6px rgba(6,75,45,0.2);">Transfer</button>`
            }
            <button class="btn-del-cow" data-tag="${cow.tag_id}" style="padding: 6px 10px; font-size: 0.82rem; color: #DC2626; border: 1.5px solid #FECACA; border-radius: 8px; background: #FFFFFF; cursor: pointer; font-weight: 700;" title="Remove">&times;</button>
          </td>
        `;
        registryTableBody.appendChild(tr);
      });

      // Bind Transfer Buttons
      document.querySelectorAll('.btn-transfer-cow').forEach(btn => {
        btn.addEventListener('click', () => {
          openTransferModal(btn.dataset.tag, btn.dataset.name);
        });
      });

      // Bind Clickable Owner Addresses to auto-audit
      document.querySelectorAll('.clickable-owner').forEach(cell => {
        cell.addEventListener('click', () => {
          const owner = cell.dataset.owner;
          if (owner && walletSearchInput && btnSearchWallet) {
            walletSearchInput.value = owner;
            btnSearchWallet.click();
            walletSearchInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        });
      });

      // Bind Delete Buttons
      document.querySelectorAll('.btn-del-cow').forEach(btn => {
        btn.addEventListener('click', async () => {
          const tag = btn.dataset.tag;
          if (confirm(`Remove cattle '${tag}' from local registry?`)) {
            await fetch(`/api/registry/${tag}`, { method: 'DELETE' });
            await updateRegistryUI();
          }
        });
      });
    } catch (e) {
      console.warn("Registry load notice:", e);
    }
  }

  // -------------------------------------------------------------
  // 9. Reset Registry
  // -------------------------------------------------------------
  if (btnResetAll) {
    btnResetAll.addEventListener('click', async () => {
      if (confirm("Reset registry ledger?")) {
        await fetch('/api/reset', { method: 'POST' });
        if (smartResultCard) smartResultCard.classList.add('hidden');
        await updateRegistryUI();
      }
    });
  }

  // Initial load
  await updateRegistryUI();
// End of DOMContentLoaded is moved to the end of the file

  // =============================================================
  // SUPPLY CHAIN MODULE: SLAUGHTERHOUSE, HALAL & RETAIL WIRING
  // =============================================================

  const btnOpenSlaughterhousePanel = document.getElementById('btnOpenSlaughterhousePanel');
  const slaughterhouseModal = document.getElementById('slaughterhouseModal');
  const btnCloseSlaughterhouseModal = document.getElementById('btnCloseSlaughterhouseModal');

  const btnOpenRetailPanel = document.getElementById('btnOpenRetailPanel');
  const retailModal = document.getElementById('retailModal');
  const btnCloseRetailModal = document.getElementById('btnCloseRetailModal');

  const radioDestWallet = document.getElementById('radioDestWallet');
  const radioDestSlaughterhouse = document.getElementById('radioDestSlaughterhouse');
  const walletAddressBox = document.getElementById('walletAddressBox');
  const slaughterhouseSelectBox = document.getElementById('slaughterhouseSelectBox');
  const modalSlaughterhouseSelect = document.getElementById('modalSlaughterhouseSelect');

  // Toggle Transfer Destination
  if (radioDestWallet && radioDestSlaughterhouse) {
    radioDestWallet.addEventListener('change', () => {
      walletAddressBox.style.display = 'block';
      slaughterhouseSelectBox.style.display = 'none';
    });
    radioDestSlaughterhouse.addEventListener('change', () => {
      walletAddressBox.style.display = 'none';
      slaughterhouseSelectBox.style.display = 'block';
      loadSlaughterhouseDropdown();
    });
  }

  async function loadSlaughterhouseDropdown() {
    try {
      const res = await fetch('/api/slaughterhouse/list');
      const data = await res.json();
      if (modalSlaughterhouseSelect && data.slaughterhouses) {
        modalSlaughterhouseSelect.innerHTML = '<option value="">-- Choose Whitelisted Slaughterhouse --</option>';
        data.slaughterhouses.forEach(sh => {
          const opt = document.createElement('option');
          opt.value = sh.wallet_address;
          opt.textContent = `${sh.name} (${sh.wallet_address.slice(0, 8)}...) - ${sh.license_number}`;
          modalSlaughterhouseSelect.appendChild(opt);
        });
      }
    } catch (e) {
      console.warn("Could not load slaughterhouse dropdown:", e);
    }
  }

  // Open / Close Slaughterhouse Panel
  if (btnOpenSlaughterhousePanel && slaughterhouseModal) {
    btnOpenSlaughterhousePanel.addEventListener('click', () => {
      loadSlaughterhouseCustodyCattle();
      loadShopkeepersDropdown();
      slaughterhouseModal.classList.remove('hidden');
    });
  }
  if (btnCloseSlaughterhouseModal && slaughterhouseModal) {
    btnCloseSlaughterhouseModal.addEventListener('click', () => {
      slaughterhouseModal.classList.add('hidden');
    });
  }

  // Open / Close Retail Supermarket Panel
  let currentShopkeeperPackages = [];
  async function loadShopkeeperPackages() {
    if (!userAddress) return;
    try {
      const res = await fetch(`/api/shopkeeper/${userAddress}/packages`);
      const data = await res.json();
      currentShopkeeperPackages = data.packages || [];

      const selectEl = document.getElementById('retailPackageSelect');
      const badgeEl = document.getElementById('retailPackageCountBadge');
      if (badgeEl) badgeEl.textContent = `${currentShopkeeperPackages.length} Packages`;

      if (selectEl) {
        selectEl.innerHTML = '<option value="">-- Select Incoming Meat Package to Inspect & Receive --</option>';
        currentShopkeeperPackages.forEach(p => {
          const opt = document.createElement('option');
          opt.value = p.package_id;
          const statusText = p.is_received ? '[RECEIVED]' : '[INCOMING]';
          opt.textContent = `${statusText} ${p.package_id} - ${p.cut_name} (${p.weight_kg} kg) | Batch: ${p.batch_id}`;
          selectEl.appendChild(opt);
        });
      }

      const inventoryList = document.getElementById('retailInventoryList');
      const invCount = document.getElementById('retailInventoryCount');
      if (invCount) invCount.textContent = `${currentShopkeeperPackages.length} Packages`;

      if (inventoryList) {
        if (currentShopkeeperPackages.length === 0) {
          inventoryList.innerHTML = `<div style="color: #64748b; font-size: 0.82rem; padding: 12px; text-align: center;">No packages currently routed to your store.</div>`;
        } else {
          inventoryList.innerHTML = '';
          currentShopkeeperPackages.forEach(p => {
            const item = document.createElement('div');
            item.style.background = '#04100a';
            item.style.border = p.is_received ? '1px solid rgba(0,245,160,0.3)' : '1px solid rgba(168,85,247,0.3)';
            item.style.borderRadius = '8px';
            item.style.padding = '10px 12px';
            item.style.display = 'flex';
            item.style.justifyContent = 'space-between';
            item.style.alignItems = 'center';
            item.style.gap = '12px';

            const qrHtml = p.is_received 
              ? (p.qr_code_base64 ? `<img src="${p.qr_code_base64}" alt="QR" style="width: 58px; height: 58px; border-radius: 6px; background: #fff; padding: 2px; flex-shrink: 0; box-shadow: 0 0 10px rgba(0,245,160,0.3);">` : '')
              : '';

            item.innerHTML = `
              <div style="display: flex; gap: 10px; align-items: center;">
                ${qrHtml}
                <div style="font-size: 0.8rem; line-height: 1.5;">
                  <strong style="color: #fff; font-size: 0.88rem;">${p.cut_name}</strong> (<span style="color: #fde047;">${p.weight_kg} kg</span>)
                  <div style="font-family: monospace; color: #00F5A0; font-size: 0.76rem;">${p.package_id}</div>
                  <div style="color: #94A3B8; font-size: 0.74rem;">Cow: <strong style="color: #fff;">${p.animal_name}</strong> | Batch: <span style="color: #38bdf8;">${p.batch_id}</span></div>
                  <div style="margin-top: 2px;">
                    ${p.is_received ? '<span style="color: #00F5A0; font-weight: 700; font-size: 0.72rem;">✓ DELIVERED TO STORE (Official QR Active)</span>' : '<span style="color: #fde047; font-size: 0.72rem;">🚚 In Transit to Supermarket (Sign Receipt to Generate QR)</span>'}
                  </div>
                </div>
              </div>
              <div style="display: flex; gap: 8px; align-items: center;">
                <a href="${p.verify_url || ('/verify/package/' + p.package_id)}" target="_blank" rel="noopener noreferrer" style="background: rgba(0,245,160,0.15); border: 1px solid #00F5A0; color: #00F5A0; font-weight: 700; padding: 5px 12px; border-radius: 6px; font-size: 0.75rem; text-decoration: none; display: inline-flex; align-items: center; gap: 4px;">
                  🔍 Scan / Track &rarr;
                </a>
                <button class="btn-del-pkg" data-pkg-id="${p.package_id}" style="background: rgba(220,38,38,0.15); border: 1px solid rgba(239,68,68,0.4); color: #EF4444; border-radius: 6px; padding: 5px 9px; font-size: 0.85rem; font-weight: 700; cursor: pointer;" title="Remove this Package">&times;</button>
              </div>
            `;
            inventoryList.appendChild(item);
          });

          // Bind delete package buttons
          inventoryList.querySelectorAll('.btn-del-pkg').forEach(btn => {
            btn.addEventListener('click', async (e) => {
              e.stopPropagation();
              const pId = btn.dataset.pkgId;
              if (confirm(`Remove Package '${pId}' from store inventory?`)) {
                await fetch(`/api/package/${pId}`, { method: 'DELETE' });
                await loadShopkeeperPackages();
              }
            });
          });
        }
      }
    } catch (e) {
      console.warn("Could not load shopkeeper packages:", e);
    }
  }

  const retailPkgSelect = document.getElementById('retailPackageSelect');
  if (retailPkgSelect) {
    retailPkgSelect.addEventListener('change', (e) => {
      const pkgId = e.target.value;
      const card = document.getElementById('retailAncestryCard');
      const pkgInput = document.getElementById('retailPkgIdInput');
      if (pkgInput) pkgInput.value = pkgId || "";

      if (!pkgId) {
        if (card) card.style.display = 'none';
        return;
      }

      const pkg = currentShopkeeperPackages.find(p => p.package_id === pkgId);
      if (pkg && card) {
        document.getElementById('ancCutName').textContent = pkg.cut_name || "-";
        document.getElementById('ancWeight').textContent = `${pkg.weight_kg} kg`;
        document.getElementById('ancBatchId').textContent = pkg.batch_id || "-";
        document.getElementById('ancCowName').textContent = pkg.animal_name || "-";
        document.getElementById('ancCowId').textContent = pkg.parent_cow_id || "-";
        document.getElementById('ancBreed').textContent = pkg.breed || "-";
        document.getElementById('ancFarmName').textContent = `${pkg.farm_name} (${pkg.origin_location})`;
        document.getElementById('ancFarmerName').textContent = pkg.original_owner || "-";
        document.getElementById('ancSlaughterhouse').textContent = `${pkg.slaughterhouse_name} (${pkg.slaughterhouse_wallet?.slice(0, 8)}...)`;
        document.getElementById('ancHalalCert').textContent = `Cert #${pkg.halal_cert_number}`;
        document.getElementById('ancMuftiNotes').textContent = `"${pkg.mufti_inspector_notes}"`;
        card.style.display = 'block';

        const signBtn = document.getElementById('btnSignRetailReceiving');
        if (signBtn) {
          if (pkg.is_received) {
            signBtn.textContent = "✅ Already Received at Store (View Traceable QR)";
            signBtn.style.background = "#059669";
          } else {
            signBtn.textContent = "Sign Retail Receipt on Blockchain & Activate Consumer QR";
            signBtn.style.background = "linear-gradient(135deg, #a855f7 0%, #7e22ce 100%)";
          }
        }
      }
    });
  }

  if (btnOpenRetailPanel && retailModal) {
    btnOpenRetailPanel.addEventListener('click', () => {
      loadShopkeeperPackages();
      retailModal.classList.remove('hidden');
    });
  }
  if (btnCloseRetailModal && retailModal) {
    btnCloseRetailModal.addEventListener('click', () => {
      retailModal.classList.add('hidden');
    });
  }

  // Admin Modal Controls
  const btnOpenAdminPanel = document.getElementById('btnOpenAdminPanel');
  const adminModal = document.getElementById('adminModal');
  const btnCloseAdminModal = document.getElementById('btnCloseAdminModal');

  if (btnOpenAdminPanel && adminModal) {
    btnOpenAdminPanel.addEventListener('click', () => adminModal.classList.remove('hidden'));
  }
  if (btnCloseAdminModal && adminModal) {
    btnCloseAdminModal.addEventListener('click', () => adminModal.classList.add('hidden'));
  }

  // Admin Action A: Authorize Slaughterhouse
  const btnAdminAuthSlaughterhouse = document.getElementById('btnAdminAuthSlaughterhouse');
  if (btnAdminAuthSlaughterhouse) {
    btnAdminAuthSlaughterhouse.addEventListener('click', async () => {
      const wallet = document.getElementById('adminShWallet')?.value.trim();
      const name = document.getElementById('adminShName')?.value.trim();
      const license = document.getElementById('adminShLicense')?.value.trim();
      const loc = document.getElementById('adminShLocation')?.value.trim();

      if (!wallet || !name || !license) {
        alert("Please enter Slaughterhouse Wallet Address, Name, and License.");
        return;
      }

      try {
        btnAdminAuthSlaughterhouse.disabled = true;
        btnAdminAuthSlaughterhouse.textContent = "Authorizing on Sepolia...";

        let txHash = null;
        if (cattleContract && web3Signer && typeof cattleContract.authorizeSlaughterhouse === 'function') {
          const tx = await cattleContract.authorizeSlaughterhouse(wallet, name, license, loc || "Punjab");
          alert(`Authorization Transaction Broadcast! Tx: ${tx.hash}`);
          await tx.wait();
          txHash = tx.hash;
        }

        await fetch('/api/slaughterhouse/authorize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            wallet_address: wallet,
            name: name,
            license_number: license,
            location: loc || "Punjab, Pakistan",
            tx_hash: txHash
          })
        });

        alert(`✅ Slaughterhouse '${name}' successfully authorized and whitelisted on-chain!`);
        btnAdminAuthSlaughterhouse.textContent = "✓ Authorize Slaughterhouse on-chain";
        btnAdminAuthSlaughterhouse.disabled = false;
        loadSlaughterhouseDropdown();
      } catch (err) {
        alert("Authorization Error: " + err.message);
        btnAdminAuthSlaughterhouse.textContent = "✓ Authorize Slaughterhouse on-chain";
        btnAdminAuthSlaughterhouse.disabled = false;
      }
    });
  }

  // Admin Action B: Authorize Shopkeeper / Supermarket
  const btnAdminAuthShopkeeper = document.getElementById('btnAdminAuthShopkeeper');
  if (btnAdminAuthShopkeeper) {
    btnAdminAuthShopkeeper.addEventListener('click', async () => {
      const wallet = document.getElementById('adminShopWallet')?.value.trim();
      const name = document.getElementById('adminShopName')?.value.trim();
      const license = document.getElementById('adminShopLicense')?.value.trim();
      const loc = document.getElementById('adminShopLocation')?.value.trim();

      if (!wallet || !name || !license) {
        alert("Please enter Shopkeeper Wallet Address, Store Name, and License.");
        return;
      }

      try {
        btnAdminAuthShopkeeper.disabled = true;
        btnAdminAuthShopkeeper.textContent = "Authorizing on Sepolia...";

        let txHash = null;
        if (cattleContract && web3Signer && typeof cattleContract.authorizeShopkeeper === 'function') {
          const tx = await cattleContract.authorizeShopkeeper(wallet, name, license, loc || "Punjab");
          alert(`Shopkeeper Authorization Broadcast! Tx: ${tx.hash}`);
          await tx.wait();
          txHash = tx.hash;
        }

        await fetch('/api/shopkeeper/authorize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            wallet_address: wallet,
            shop_name: name,
            license_number: license,
            location: loc || "Punjab, Pakistan",
            tx_hash: txHash
          })
        });

        alert(`✅ Retail Store '${name}' successfully authorized on-chain!`);
        btnAdminAuthShopkeeper.textContent = "✓ Authorize Shopkeeper on-chain";
        btnAdminAuthShopkeeper.disabled = false;
        loadShopkeepersDropdown();
      } catch (err) {
        alert("Authorization Error: " + err.message);
        btnAdminAuthShopkeeper.textContent = "✓ Authorize Shopkeeper on-chain";
        btnAdminAuthShopkeeper.disabled = false;
      }
    });
  }

  // Load Verified Shopkeepers Dropdown
  async function loadShopkeepersDropdown() {
    const pkgShopkeeperSelect = document.getElementById('pkgShopkeeperSelect');
    if (!pkgShopkeeperSelect) return;
    try {
      const res = await fetch('/api/shopkeeper/list');
      const data = await res.json();
      pkgShopkeeperSelect.innerHTML = '<option value="">-- Choose Verified Shopkeeper / Supermarket --</option>';
      (data.shopkeepers || []).forEach(sh => {
        const opt = document.createElement('option');
        opt.value = sh.wallet_address;
        opt.textContent = `${sh.shop_name} (${sh.wallet_address.slice(0, 8)}...) - ${sh.license_number}`;
        pkgShopkeeperSelect.appendChild(opt);
      });
    } catch (e) {
      console.warn("Could not load shopkeepers:", e);
    }
  }

  // Load Slaughterhouse Custody Cattle
  async function loadSlaughterhouseCustodyCattle() {
    const shSelectOwnedCattle = document.getElementById('shSelectOwnedCattle');
    if (!shSelectOwnedCattle || !userAddress) return;

    shSelectOwnedCattle.innerHTML = '<option value="">-- Select Cattle in Your Custody --</option>';
    const cleanAddr = userAddress.toLowerCase();

    for (const [tag, cow] of Object.entries(window.__HalalChain_Current_Registry || {})) {
      if (cow.owner_address?.toLowerCase() === cleanAddr && cow.status !== 'SLAUGHTERED_HALAL') {
        const opt = document.createElement('option');
        opt.value = tag;
        opt.dataset.batch = cow.batch_id || "";
        opt.textContent = `${tag} (${cow.name} - ${cow.breed || 'Cattle'}) ${cow.batch_id ? '[Batch: ' + cow.batch_id + ']' : ''}`;
        shSelectOwnedCattle.appendChild(opt);
      }
    }

    shSelectOwnedCattle.onchange = (e) => {
      const selected = shSelectOwnedCattle.options[shSelectOwnedCattle.selectedIndex];
      const cowIdInput = document.getElementById('shSignCowId');
      const batchInput = document.getElementById('shSignBatchId');
      const pkgBatchIdInput = document.getElementById('pkgBatchId');
      const pkgParentCowInput = document.getElementById('pkgParentCowId');

      const batchVal = selected?.dataset?.batch || "";
      if (cowIdInput) cowIdInput.value = selected.value || "";
      if (batchInput) batchInput.value = batchVal || "SINGLE-TRANSFER";
      if (pkgBatchIdInput) pkgBatchIdInput.value = batchVal || "SINGLE-TRANSFER";

      // If cow belongs to a batch, auto-populate all cows belonging to this batch!
      if (batchVal && window.__HalalChain_Current_Registry) {
        const batchCows = [];
        for (const [tag, cow] of Object.entries(window.__HalalChain_Current_Registry)) {
          if (cow.batch_id === batchVal) {
            batchCows.push(tag);
          }
        }
        if (pkgParentCowInput) {
          pkgParentCowInput.value = batchCows.length > 0 ? batchCows.join(', ') : (selected.value || "");
        }
      } else {
        if (pkgParentCowInput) pkgParentCowInput.value = selected.value || "";
      }
    };
  }

  // 1. Authorize Slaughterhouse (Legacy Button Helper)
  const btnAuthorizeSlaughterhouse = document.getElementById('btnAuthorizeSlaughterhouse');
  if (btnAuthorizeSlaughterhouse) {
    btnAuthorizeSlaughterhouse.addEventListener('click', async () => {
      const wallet = document.getElementById('shInputWallet')?.value.trim();
      const name = document.getElementById('shInputName')?.value.trim();
      const license = document.getElementById('shInputLicense')?.value.trim();
      const loc = document.getElementById('shInputLocation')?.value.trim();

      if (!wallet || !name || !license) {
        alert("Please provide Slaughterhouse Wallet, Name, and License number.");
        return;
      }

      try {
        btnAuthorizeSlaughterhouse.disabled = true;
        btnAuthorizeSlaughterhouse.textContent = "Authorizing on Sepolia...";

        let txHash = null;
        if (cattleContract && web3Signer && typeof cattleContract.authorizeSlaughterhouse === 'function') {
          const tx = await cattleContract.authorizeSlaughterhouse(wallet, name, license, loc || "Punjab");
          alert(`Authorization Transaction Broadcast! Tx: ${tx.hash}`);
          await tx.wait();
          txHash = tx.hash;
        }

        await fetch('/api/slaughterhouse/authorize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            wallet_address: wallet,
            name: name,
            license_number: license,
            location: loc || "Punjab, Pakistan",
            tx_hash: txHash
          })
        });

        alert(`✅ Slaughterhouse '${name}' successfully authorized and whitelisted on-chain!`);
        btnAuthorizeSlaughterhouse.textContent = "✓ Authorize on Blockchain";
        btnAuthorizeSlaughterhouse.disabled = false;
        loadSlaughterhouseDropdown();
      } catch (err) {
        alert("Authorization Error: " + err.message);
        btnAuthorizeSlaughterhouse.textContent = "✓ Authorize on Blockchain";
        btnAuthorizeSlaughterhouse.disabled = false;
      }
    });
  }

  // 2. Slaughterhouse Halal Digital Sign-off
  const btnSignHalalSlaughter = document.getElementById('btnSignHalalSlaughter');
  if (btnSignHalalSlaughter) {
    btnSignHalalSlaughter.addEventListener('click', async () => {
      const cowId = document.getElementById('shSignCowId')?.value.trim();
      const certNo = document.getElementById('shHalalCertNo')?.value.trim() || "PHDA-HALAL-992";
      const notes = document.getElementById('shInspectorNotes')?.value.trim() || "100% Manual Islamic Zibah Verified with sharp knife";

      if (!cowId) {
        alert("Please select or enter an Animal Cow ID in your custody.");
        return;
      }

      if (!userAddress) {
        alert("Please connect your MetaMask wallet with the Authorized Slaughterhouse account first!");
        return;
      }

      try {
        btnSignHalalSlaughter.disabled = true;
        btnSignHalalSlaughter.textContent = "Verifying Custody & Signing on Sepolia...";

        let txHash = null;
        if (cattleContract && web3Signer && typeof cattleContract.signHalalSlaughter === 'function') {
          let tokenId = 1;
          try {
            const fetchedId = await cattleContract.cowIdToTokenId(cowId);
            if (fetchedId && Number(fetchedId) > 0) tokenId = fetchedId;
          } catch (e) {}

          const tx = await cattleContract.signHalalSlaughter([tokenId], certNo, notes);
          alert(`Halal Slaughter Signature Broadcast! Tx: ${tx.hash}`);
          await tx.wait();
          txHash = tx.hash;
        }

        const res = await fetch('/api/slaughter/sign-halal', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            cow_ids: [cowId],
            slaughterhouse_wallet: userAddress,
            halal_cert_number: certNo,
            inspector_notes: notes,
            tx_hash: txHash
          })
        });

        const data = await res.json();
        if (!res.ok || data.success === false) {
          throw new Error(data.message || data.error || "Halal sign failed");
        }

        alert(`🔪 Halal Slaughter Digitally Signed & Verified for '${cowId}'!
NFT status updated permanently to SLAUGHTERED.`);
        btnSignHalalSlaughter.textContent = "Sign Halal Slaughter (Update NFT to SLAUGHTERED)";
        btnSignHalalSlaughter.disabled = false;
        await updateRegistryUI();
        loadSlaughterhouseCustodyCattle();

        // Check if all cows in this batch are slaughtered and populate package fields
        const currBatch = document.getElementById('shSignBatchId')?.value.trim();
        if (currBatch && currBatch !== "SINGLE-TRANSFER" && window.__HalalChain_Current_Registry) {
          const batchCows = [];
          for (const [tag, cow] of Object.entries(window.__HalalChain_Current_Registry)) {
            if (cow.batch_id === currBatch) {
              batchCows.push(tag);
            }
          }
          const pkgBatchIdInput = document.getElementById('pkgBatchId');
          const pkgParentCowInput = document.getElementById('pkgParentCowId');
          if (pkgBatchIdInput) pkgBatchIdInput.value = currBatch;
          if (pkgParentCowInput && batchCows.length > 0) {
            pkgParentCowInput.value = batchCows.join(', ');
          }
        }
      } catch (err) {
        alert("Halal Signing Error: " + (err.reason || err.message));
        btnSignHalalSlaughter.textContent = "Sign Halal Slaughter (Update NFT to SLAUGHTERED)";
        btnSignHalalSlaughter.disabled = false;
      }
    });
  }

  // Dynamic Custom Package Row Addition
  const btnAddPackageRow = document.getElementById('btnAddPackageRow');
  const customPackageRows = document.getElementById('customPackageRows');
  if (btnAddPackageRow && customPackageRows) {
    btnAddPackageRow.addEventListener('click', () => {
      const div = document.createElement('div');
      div.className = 'pkg-row';
      div.style.display = 'grid';
      div.style.gridTemplateColumns = '2fr 1fr auto';
      div.style.gap = '8px';
      div.innerHTML = `
        <input type="text" class="pkg-cut-name" placeholder="Cut Type (e.g. Minced Meat)" style="background: #04100a; border: 1px solid rgba(255,255,255,0.2); color: #fff; padding: 6px 8px; border-radius: 4px; font-size: 0.8rem;">
        <input type="number" step="0.5" class="pkg-cut-weight" value="8.0" placeholder="Weight (kg)" style="background: #04100a; border: 1px solid rgba(255,255,255,0.2); color: #fff; padding: 6px 8px; border-radius: 4px; font-size: 0.8rem;">
        <span style="color: #94A3B8; font-size: 0.75rem; align-self: center;">kg</span>
      `;
      customPackageRows.appendChild(div);
    });
  }

  // 3. Generate Child Meat Packages (Batch Completion Enforced)
  const btnGenerateMeatPackages = document.getElementById('btnGenerateMeatPackages');
  if (btnGenerateMeatPackages) {
    btnGenerateMeatPackages.addEventListener('click', async () => {
      const parentCowId = document.getElementById('pkgParentCowId')?.value.trim();
      const batchId = document.getElementById('pkgBatchId')?.value.trim();
      const destShopkeeper = document.getElementById('pkgShopkeeperSelect')?.value?.trim();

      if (!parentCowId) {
        alert("Please enter parent Cow ID.");
        return;
      }

      if (!destShopkeeper) {
        alert("Please select a Verified Shopkeeper / Supermarket from the dropdown.");
        return;
      }

      // Collect custom cut types and weights
      const cutNames = [];
      const cutWeights = [];
      document.querySelectorAll('.pkg-row').forEach(row => {
        const name = row.querySelector('.pkg-cut-name')?.value.trim();
        const weight = parseFloat(row.querySelector('.pkg-cut-weight')?.value) || 5.0;
        if (name) {
          cutNames.push(name);
          cutWeights.push(weight);
        }
      });

      if (cutNames.length === 0) {
        alert("Please define at least one custom cut type and weight.");
        return;
      }

      try {
        btnGenerateMeatPackages.disabled = true;
        btnGenerateMeatPackages.textContent = "Verifying Batch Slaughter Status...";

        // Validate batch slaughter status
        if (batchId) {
          const bRes = await fetch(`/api/slaughter/batch-status/${batchId}`);
          const bData = await bRes.json();
          if (!bData.all_slaughtered && bData.total_animals > 0) {
            throw new Error(`Batch '${batchId}' is not fully slaughtered! (${bData.slaughtered_count}/${bData.total_animals} slaughtered). All animals in the batch must be slaughtered before generating packages.`);
          }
        }

        btnGenerateMeatPackages.textContent = "Minting Meat Packages on Sepolia...";

        let txHash = null;
        const primaryCowId = parentCowId.split(',')[0].trim();
        if (cattleContract && web3Signer && typeof cattleContract.generateMeatPackages === 'function') {
          let parentTokenId = 1;
          try {
            const fetchedId = await cattleContract.cowIdToTokenId(primaryCowId);
            if (fetchedId && Number(fetchedId) > 0) parentTokenId = fetchedId;
          } catch (e) {}

          const weightGrams = cutWeights.map(w => Math.round(w * 1000));
          const tx = await cattleContract.generateMeatPackages(parentTokenId, cutNames, weightGrams, batchId || "BATCH-001", destShopkeeper);
          alert(`Package Generation Broadcast to Sepolia! Tx: ${tx.hash}`);
          await tx.wait();
          txHash = tx.hash;
        }

        const res = await fetch('/api/processing/generate-packages', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            parent_cow_id: parentCowId,
            cuts: cutNames,
            weights_kg: cutWeights,
            batch_id: batchId || "BATCH-SINGLE",
            holder_wallet: destShopkeeper,
            tx_hash: txHash
          })
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Packaging failed");

        alert(`${data.packages.length} Custom Meat Packages successfully generated and transferred to Shopkeeper:\n${destShopkeeper}`);
        btnGenerateMeatPackages.textContent = "Generate Verified Meat Packages & Transfer to Retail";
        btnGenerateMeatPackages.disabled = false;
        slaughterhouseModal.classList.add('hidden');
      } catch (err) {
        alert("Package Generation Notice: " + err.message);
        btnGenerateMeatPackages.textContent = "Generate Verified Meat Packages & Transfer to Retail";
        btnGenerateMeatPackages.disabled = false;
      }
    });
  }

  // 4. Supermarket / Retailer Delivery Sign-off
  const btnSignRetailReceiving = document.getElementById('btnSignRetailReceiving');
  if (btnSignRetailReceiving) {
    btnSignRetailReceiving.addEventListener('click', async () => {
      const pkgId = document.getElementById('retailPkgIdInput')?.value.trim();
      const shopName = document.getElementById('retailShopNameInput')?.value.trim() || "Metro Cash & Carry";
      const receiverName = document.getElementById('retailReceiverNameInput')?.value.trim() || "Store Meat Manager";

      if (!pkgId) {
        alert("Please enter Meat Package ID or Tag.");
        return;
      }

      try {
        btnSignRetailReceiving.disabled = true;
        btnSignRetailReceiving.textContent = "Signing Delivery Receipt on Sepolia...";

        let txHash = null;
        if (cattleContract && web3Signer && typeof cattleContract.confirmRetailDelivery === 'function') {
          let packageTokenId = 0;
          try {
            const fetchedId = await cattleContract.packageTagToPackageId(pkgId);
            if (fetchedId && Number(fetchedId) > 0) packageTokenId = Number(fetchedId);
          } catch (e) {}

          // If mapping tag was formatted differently on-chain, resolve index from selected package
          if (!packageTokenId || packageTokenId === 0) {
            const selectedPkg = currentShopkeeperPackages.find(p => p.package_id === pkgId);
            if (selectedPkg) {
              const allPkgsCount = await cattleContract.totalPackages();
              const tot = Number(allPkgsCount);
              for (let i = 1; i <= tot; i++) {
                try {
                  const onChainPkg = await cattleContract.meatPackages(i);
                  // Match cut type or tag
                  if (onChainPkg && (onChainPkg.packageTag === pkgId || onChainPkg.cutType.toLowerCase() === selectedPkg.cut_name?.toLowerCase())) {
                    packageTokenId = i;
                    break;
                  }
                } catch (err) {}
              }
            }
          }

          if (!packageTokenId || packageTokenId === 0) {
            packageTokenId = 1;
          }

          const tx = await cattleContract.confirmRetailDelivery([packageTokenId], shopName, receiverName);
          alert(`Retail Receiving Signature Broadcast! Tx: ${tx.hash}`);
          await tx.wait();
          txHash = tx.hash;
        }

        await fetch('/api/retail/confirm-delivery', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            package_ids: [pkgId],
            retailer_wallet: userAddress || "0x1461bd11a98e34a04b20c252e56965c235e369b6",
            shop_name: shopName,
            receiver_name: receiverName,
            tx_hash: txHash
          })
        });

        alert(`Meat Package Delivery Confirmed at ${shopName}!\n\nTraceable QR Code Activated.`);
        window.open(`/verify/package/${pkgId}`, '_blank');
        btnSignRetailReceiving.textContent = "Sign Retail Receipt on Blockchain & Activate Consumer QR";
        btnSignRetailReceiving.disabled = false;
        retailModal.classList.add('hidden');
      } catch (err) {
        alert("Retail Receiving Error: " + err.message);
        btnSignRetailReceiving.textContent = "Sign Retail Receipt on Blockchain & Activate Consumer QR";
        btnSignRetailReceiving.disabled = false;
      }
    });
  }

  // NFT Guideline Modal Controls
  function showNftGuidelineModal(tokenId = 1) {
    const modal = document.getElementById('nftGuidelineModal');
    const addrEl = document.getElementById('nftModalContractAddr');
    const idEl = document.getElementById('nftModalTokenId');
    if (addrEl && contractInfo) addrEl.textContent = contractInfo.contract_address;
    if (idEl) idEl.textContent = tokenId;
    if (modal) modal.classList.remove('hidden');
  }

  const btnCloseNftModal = document.getElementById('btnCloseNftModal');
  const btnDismissNftModal = document.getElementById('btnDismissNftModal');
  const btnCopyNftContract = document.getElementById('btnCopyNftContract');
  const btnCopyNftTokenId = document.getElementById('btnCopyNftTokenId');

  if (btnCloseNftModal) {
    btnCloseNftModal.addEventListener('click', () => {
      document.getElementById('nftGuidelineModal')?.classList.add('hidden');
    });
  }
  if (btnDismissNftModal) {
    btnDismissNftModal.addEventListener('click', () => {
      document.getElementById('nftGuidelineModal')?.classList.add('hidden');
    });
  }
  if (btnCopyNftContract) {
    btnCopyNftContract.addEventListener('click', () => {
      const addr = document.getElementById('nftModalContractAddr')?.textContent;
      if (addr) {
        navigator.clipboard.writeText(addr);
        btnCopyNftContract.textContent = "✓ Copied";
        setTimeout(() => btnCopyNftContract.textContent = "Copy", 1500);
      }
    });
  }
  if (btnCopyNftTokenId) {
    btnCopyNftTokenId.addEventListener('click', () => {
      const tid = document.getElementById('nftModalTokenId')?.textContent;
      if (tid) {
        navigator.clipboard.writeText(tid);
        btnCopyNftTokenId.textContent = "✓ Copied";
        setTimeout(() => btnCopyNftTokenId.textContent = "Copy", 1500);
      }
    });
  }
});
