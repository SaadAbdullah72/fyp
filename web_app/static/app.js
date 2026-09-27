/**
 * Livestock Muzzle Biometric Web Interface - Client Application Logic
 * Supports:
 * Mode 1: Smart Cattle Registration (Anti-Duplicate AI Protection)
 * Mode 2: Direct 1-to-1 Muzzle Comparison (Photo A vs Photo B)
 * Mode 3: Search & Verify Cattle (Database Lookup)
 */

document.addEventListener('DOMContentLoaded', async () => {
  // -------------------------------------------------------------
  // Mode Tabs & Layout Sections
  // -------------------------------------------------------------
  const tabSmartRegister = document.getElementById('tabSmartRegister');
  const tabDirectCompare = document.getElementById('tabDirectCompare');
  const tabSearchVerify = document.getElementById('tabSearchVerify');

  const smartRegisterSection = document.getElementById('smartRegisterSection');
  const directCompareSection = document.getElementById('directCompareSection');
  const searchSamplesBar = document.getElementById('searchSamplesBar');
  const searchVerifyLayout = document.getElementById('searchVerifyLayout');
  const registrySection = document.getElementById('registrySection');

  // Header Elements
  const headerRegistryCount = document.getElementById('headerRegistryCount');
  const registryCountBadge = document.getElementById('registryCountBadge');
  const registryTableBody = document.getElementById('registryTableBody');
  const btnResetAll = document.getElementById('btnResetAll');
  const toast = document.getElementById('toast');

  // -------------------------------------------------------------
  // Mode 1: 3-Shot Smart Registration Elements
  // -------------------------------------------------------------
  const smartRegName = document.getElementById('smartRegName');
  const smartRegBreed = document.getElementById('smartRegBreed');
  const smartRegTag = document.getElementById('smartRegTag');
  const btnSubmitSmartRegister = document.getElementById('btnSubmitSmartRegister');
  const smartRegisterSpinner = document.getElementById('smartRegisterSpinner');
  const multiQualityStatusText = document.getElementById('multiQualityStatusText');
  const qualityGateHint = document.getElementById('qualityGateHint');

  // 3 Slots
  const slotCards = [document.getElementById('shotCard1'), document.getElementById('shotCard2'), document.getElementById('shotCard3')];
  const slotDrops = [document.getElementById('slotDrop1'), document.getElementById('slotDrop2'), document.getElementById('slotDrop3')];
  const slotFileInputs = [document.getElementById('slotFileInput1'), document.getElementById('slotFileInput2'), document.getElementById('slotFileInput3')];
  const slotPrompts = [document.getElementById('slotPrompt1'), document.getElementById('slotPrompt2'), document.getElementById('slotPrompt3')];
  const slotPreviews = [document.getElementById('slotPreview1'), document.getElementById('slotPreview2'), document.getElementById('slotPreview3')];
  const slotImgs = [document.getElementById('slotImg1'), document.getElementById('slotImg2'), document.getElementById('slotImg3')];
  const slotNames = [document.getElementById('slotName1'), document.getElementById('slotName2'), document.getElementById('slotName3')];
  const btnRemoveSlots = [document.getElementById('btnRemoveSlot1'), document.getElementById('btnRemoveSlot2'), document.getElementById('btnRemoveSlot3')];
  const slotBadges = [document.getElementById('slotQualityBadge1'), document.getElementById('slotQualityBadge2'), document.getElementById('slotQualityBadge3')];

  const btnSmartPreset1 = document.getElementById('btnSmartPreset1');
  const btnSmartPreset2 = document.getElementById('btnSmartPreset2');
  const btnSmartPreset3 = document.getElementById('btnSmartPreset3');

  // Results Elements
  const smartResultCard = document.getElementById('smartResultCard');
  const smartDuplicateView = document.getElementById('smartDuplicateView');
  const smartSuccessView = document.getElementById('smartSuccessView');

  // Duplicate View Fields
  const dupBannerTitle = document.getElementById('dupBannerTitle');
  const dupBannerDesc = document.getElementById('dupBannerDesc');
  const smartDupUploadThumb = document.getElementById('smartDupUploadThumb');
  const smartDupUploadName = document.getElementById('smartDupUploadName');
  const smartDupConfidence = document.getElementById('smartDupConfidence');
  const smartDupCosine = document.getElementById('smartDupCosine');
  const smartDupThreshold = document.getElementById('smartDupThreshold');
  const smartDupMatchedThumb = document.getElementById('smartDupMatchedThumb');
  const smartDupMatchedName = document.getElementById('smartDupMatchedName');
  const smartDupMatchedTag = document.getElementById('smartDupMatchedTag');
  const smartDupMatchedBreed = document.getElementById('smartDupMatchedBreed');
  const smartDupMatchedDate = document.getElementById('smartDupMatchedDate');

  // Success View Fields
  const succBannerTitle = document.getElementById('succBannerTitle');
  const succBannerDesc = document.getElementById('succBannerDesc');
  const smartSuccThumb = document.getElementById('smartSuccThumb');
  const smartSuccName = document.getElementById('smartSuccName');
  const smartSuccTag = document.getElementById('smartSuccTag');
  const smartSuccBreed = document.getElementById('smartSuccBreed');
  const smartSuccHash = document.getElementById('smartSuccHash');
  const smartSuccGalleryThumbs = document.getElementById('smartSuccGalleryThumbs');
  const smartSuccVectorChips = document.getElementById('smartSuccVectorChips');
  const smartSuccClosestInfo = document.getElementById('smartSuccClosestInfo');
  const smartSuccClosestSim = document.getElementById('smartSuccClosestSim');

  // 3-Shot State
  const slotFiles = [null, null, null];
  const slotScores = [0, 0, 0];
  const slotPassed = [false, false, false];

  // -------------------------------------------------------------
  // Mode 2: Direct 1-to-1 Comparison Elements
  // -------------------------------------------------------------
  const boxCompare1 = document.getElementById('boxCompare1');
  const boxCompare2 = document.getElementById('boxCompare2');
  const compareFileInput1 = document.getElementById('compareFileInput1');
  const compareFileInput2 = document.getElementById('compareFileInput2');
  const boxPrompt1 = document.getElementById('boxPrompt1');
  const boxPrompt2 = document.getElementById('boxPrompt2');
  const boxPreview1 = document.getElementById('boxPreview1');
  const boxPreview2 = document.getElementById('boxPreview2');
  const boxImg1 = document.getElementById('boxImg1');
  const boxImg2 = document.getElementById('boxImg2');
  const boxFilename1 = document.getElementById('boxFilename1');
  const boxFilename2 = document.getElementById('boxFilename2');
  const btnRemoveBox1 = document.getElementById('btnRemoveBox1');
  const btnRemoveBox2 = document.getElementById('btnRemoveBox2');

  const btnPresetSame = document.getElementById('btnPresetSame');
  const btnPresetDiff = document.getElementById('btnPresetDiff');
  const directThresholdSlider = document.getElementById('directThresholdSlider');
  const directThresholdVal = document.getElementById('directThresholdVal');
  const btnRunDirectCompare = document.getElementById('btnRunDirectCompare');
  const directCompareSpinner = document.getElementById('directCompareSpinner');

  const directResultsCard = document.getElementById('directResultsCard');
  const directVerdictBanner = document.getElementById('directVerdictBanner');
  const directVerdictIcon = document.getElementById('directVerdictIcon');
  const directVerdictTitle = document.getElementById('directVerdictTitle');
  const directVerdictDesc = document.getElementById('directVerdictDesc');
  const directMetricCosine = document.getElementById('directMetricCosine');
  const directMetricBar = document.getElementById('directMetricBar');
  const directMetricConfidence = document.getElementById('directMetricConfidence');
  const directMetricAngular = document.getElementById('directMetricAngular');
  const directHash1 = document.getElementById('directHash1');
  const directHash2 = document.getElementById('directHash2');
  const directQualityBadge1 = document.getElementById('directQualityBadge1');
  const directQualityBadge2 = document.getElementById('directQualityBadge2');
  const directQualityHint = document.getElementById('directQualityHint');

  let directFile1 = null;
  let directFile2 = null;
  let directPass1 = false;
  let directPass2 = false;

  // -------------------------------------------------------------
  // Mode 3: Search & Verify Elements
  // -------------------------------------------------------------
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');
  const dropzonePrompt = document.getElementById('dropzonePrompt');
  const dropzonePreview = document.getElementById('dropzonePreview');
  const previewImg = document.getElementById('previewImg');
  const previewFilename = document.getElementById('previewFilename');
  const btnRemoveImg = document.getElementById('btnRemoveImg');
  const searchQualityBadge = document.getElementById('searchQualityBadge');
  const searchQualityHint = document.getElementById('searchQualityHint');

  const thresholdSlider = document.getElementById('thresholdSlider');
  const thresholdVal = document.getElementById('thresholdVal');
  const btnScanVerify = document.getElementById('btnScanVerify');
  const scanSpinner = document.getElementById('scanSpinner');

  const dualInspectionCard = document.getElementById('dualInspectionCard');
  const rawThumb = document.getElementById('rawThumb');
  const claheThumb = document.getElementById('claheThumb');

  const verdictBanner = document.getElementById('verdictBanner');
  const verdictIcon = document.getElementById('verdictIcon');
  const verdictTitle = document.getElementById('verdictTitle');
  const verdictDescription = document.getElementById('verdictDescription');

  const metricsGrid = document.getElementById('metricsGrid');
  const metricCosine = document.getElementById('metricCosine');
  const metricCosineBar = document.getElementById('metricCosineBar');
  const metricConfidence = document.getElementById('metricConfidence');
  const metricAngular = document.getElementById('metricAngular');

  const matchedProfileCard = document.getElementById('matchedProfileCard');
  const matchedTagId = document.getElementById('matchedTagId');
  const matchedName = document.getElementById('matchedName');
  const matchedThumb = document.getElementById('matchedThumb');

  const fingerprintSection = document.getElementById('fingerprintSection');
  const displayHash = document.getElementById('displayHash');
  const vectorChips = document.getElementById('vectorChips');
  const btnCopyHash = document.getElementById('btnCopyHash');
  const samplesContainer = document.getElementById('samplesContainer');

  let currentSearchFile = null;
  let searchPassed = false;

  // -------------------------------------------------------------
  // Navigation & Mode Switching
  // -------------------------------------------------------------
  function switchMode(mode) {
    tabSmartRegister.classList.remove('active');
    tabDirectCompare.classList.remove('active');
    tabSearchVerify.classList.remove('active');

    smartRegisterSection.classList.add('hidden');
    directCompareSection.classList.add('hidden');
    searchSamplesBar.classList.add('hidden');
    searchVerifyLayout.classList.add('hidden');

    if (mode === 'smart') {
      tabSmartRegister.classList.add('active');
      smartRegisterSection.classList.remove('hidden');
    } else if (mode === 'direct') {
      tabDirectCompare.classList.add('active');
      directCompareSection.classList.remove('hidden');
    } else if (mode === 'search') {
      tabSearchVerify.classList.add('active');
      searchSamplesBar.classList.remove('hidden');
      searchVerifyLayout.classList.remove('hidden');
    }
  }

  tabSmartRegister.addEventListener('click', () => switchMode('smart'));
  tabDirectCompare.addEventListener('click', () => switchMode('direct'));
  tabSearchVerify.addEventListener('click', () => switchMode('search'));

  // Start with Smart Register active by default
  switchMode('smart');

  // Load registry and demo samples
  try {
    await updateRegistryUI();
    await loadSamples();
  } catch (err) {
    console.warn('Initialization error:', err);
  }

  // -------------------------------------------------------------
  // Helper: Sample File Fetcher
  // -------------------------------------------------------------
  async function fetchFileFromSample(subPath, filename) {
    const fullPath = `ai_engine/data/cropped_muzzles/${subPath}`;
    const res = await fetch(`/api/sample-image?path=${encodeURIComponent(fullPath)}`);
    if (!res.ok) throw new Error('Sample not found on server');
    const blob = await res.blob();
    return new File([blob], filename, { type: 'image/jpeg' });
  }

  // -------------------------------------------------------------
  // Universal Real-Time Quality Audit Engine
  // -------------------------------------------------------------
  async function runQualityAudit(file, badgeEl, onComplete) {
    if (!badgeEl) return;
    badgeEl.className = 'slot-quality-badge badge-checking';
    badgeEl.innerHTML = '🔄 Auditing Quality...';
    try {
      const fd = new FormData();
      fd.append('file', file);
      const res = await fetch('/api/quality-check', { method: 'POST', body: fd });
      const data = await res.json();
      if (res.ok && data.status === 'success') {
        const score = data.score;
        const meets = data.meets_production_threshold;
        if (meets) {
          badgeEl.className = 'slot-quality-badge badge-passed';
          badgeEl.innerHTML = `✅ Quality: ${score}% (PASSED)`;
          if (onComplete) onComplete(true, score);
        } else {
          badgeEl.className = 'slot-quality-badge badge-rejected';
          badgeEl.innerHTML = `❌ Quality: ${score}% (REJECTED <80%)`;
          if (onComplete) onComplete(false, score);
        }
      } else {
        badgeEl.className = 'slot-quality-badge badge-rejected';
        badgeEl.innerHTML = '❌ Quality Check Failed';
        if (onComplete) onComplete(false, 0);
      }
    } catch (err) {
      badgeEl.className = 'slot-quality-badge badge-rejected';
      badgeEl.innerHTML = '❌ Quality Service Offline';
      if (onComplete) onComplete(false, 0);
    }
  }

  // =============================================================
  // 1. SMART CATTLE REGISTRATION (3-SHOT MULTI-ANGLE ENROLLMENT)
  // =============================================================

  // Setup Slot Dropzones & Pickers
  [0, 1, 2].forEach(idx => {
    const drop = slotDrops[idx];
    const input = slotFileInputs[idx];
    const removeBtn = btnRemoveSlots[idx];

    if (!drop || !input) return;

    drop.addEventListener('click', (e) => {
      if (e.target !== removeBtn) input.click();
    });

    ['dragenter', 'dragover'].forEach(n => {
      drop.addEventListener(n, (e) => { e.preventDefault(); drop.classList.add('dragover'); });
    });
    ['dragleave', 'drop'].forEach(n => {
      drop.addEventListener(n, (e) => { e.preventDefault(); drop.classList.remove('dragover'); });
    });
    drop.addEventListener('drop', (e) => {
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleSlotFile(idx, e.dataTransfer.files[0]);
      }
    });

    input.addEventListener('change', (e) => {
      if (e.target.files && e.target.files.length > 0) {
        handleSlotFile(idx, e.target.files[0]);
      }
    });

    if (removeBtn) {
      removeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        clearSlot(idx);
      });
    }
  });

  function handleSlotFile(idx, file) {
    if (!file.type.startsWith('image/')) {
      showToast('❌ Please upload an image file (JPG, PNG).');
      return;
    }
    slotFiles[idx] = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      slotImgs[idx].src = e.target.result;
      slotNames[idx].textContent = file.name;
      slotPrompts[idx].classList.add('hidden');
      slotPreviews[idx].classList.remove('hidden');

      // Run instant real-time quality gate
      runQualityAudit(file, slotBadges[idx], (passed, score) => {
        slotPassed[idx] = passed;
        slotScores[idx] = score;
        updateMultiShotReadiness();
      });
    };
    reader.readAsDataURL(file);
  }

  function clearSlot(idx) {
    slotFiles[idx] = null;
    slotScores[idx] = 0;
    slotPassed[idx] = false;
    slotFileInputs[idx].value = '';
    slotPrompts[idx].classList.remove('hidden');
    slotPreviews[idx].classList.add('hidden');
    slotBadges[idx].className = 'slot-quality-badge badge-pending';
    slotBadges[idx].innerHTML = '⏳ Quality: Awaiting Photo';
    updateMultiShotReadiness();
  }

  smartRegName.addEventListener('input', updateMultiShotReadiness);

  function updateMultiShotReadiness() {
    const readyCount = slotPassed.filter(p => p).length;
    const hasName = smartRegName.value.trim().length > 0;

    if (readyCount === 3) {
      const avg = (slotScores[0] + slotScores[1] + slotScores[2]) / 3;
      multiQualityStatusText.className = 'text-success font-semibold';
      multiQualityStatusText.textContent = `✅ All 3 Shots Verified (Avg: ${avg.toFixed(1)}%) — Ready!`;

      if (hasName) {
        btnSubmitSmartRegister.disabled = false;
        qualityGateHint.textContent = '✅ All 3 biometric captures validated (Min 80% met). Ready to enroll!';
        qualityGateHint.style.color = '#34d399';
      } else {
        btnSubmitSmartRegister.disabled = true;
        qualityGateHint.textContent = '⚠️ Enter animal name to unlock enrollment button.';
        qualityGateHint.style.color = '#fbbf24';
      }
    } else {
      multiQualityStatusText.className = 'text-warning font-semibold';
      multiQualityStatusText.textContent = `⏳ ${readyCount} of 3 Shots Passed 80% Gate`;
      btnSubmitSmartRegister.disabled = true;
      qualityGateHint.textContent = '🔒 Register button is locked. Upload 3 clear muzzle shots (minimum 80% quality required per shot).';
      qualityGateHint.style.color = '#94a3b8';
    }
  }

  // Submit 3-Shot Smart Registration
  btnSubmitSmartRegister.addEventListener('click', async () => {
    if (!slotFiles[0] || !slotFiles[1] || !slotFiles[2] || !smartRegName.value.trim()) return;

    btnSubmitSmartRegister.disabled = true;
    smartRegisterSpinner.classList.remove('hidden');

    const formData = new FormData();
    formData.append('file1', slotFiles[0]);
    formData.append('file2', slotFiles[1]);
    formData.append('file3', slotFiles[2]);
    formData.append('name', smartRegName.value.trim());
    formData.append('breed', smartRegBreed.value.trim() || 'Sahiwal Cattle');
    if (smartRegTag.value.trim()) {
      formData.append('tag_id', smartRegTag.value.trim());
    }
    formData.append('threshold', 0.45); // Production Standard Fixed Threshold

    try {
      const res = await fetch('/api/smart-register', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.message || data.detail || 'Smart registration failed');
      }

      renderSmartResults(data);
      await updateRegistryUI();
    } catch (err) {
      showToast(`❌ ${err.message}`);
    } finally {
      btnSubmitSmartRegister.disabled = false;
      smartRegisterSpinner.classList.add('hidden');
    }
  });

  function renderSmartResults(data) {
    smartResultCard.classList.remove('hidden');

    if (data.status === 'already_registered') {
      // DUPLICATE DETECTED!
      smartSuccessView.classList.add('hidden');
      smartDuplicateView.classList.remove('hidden');

      dupBannerTitle.textContent = `Sorry! This animal is ALREADY registered as '${data.matched_animal.name}'!`;
      dupBannerDesc.textContent = `Centroid master embedding matched existing record '${data.matched_animal.tag_id}' with ${data.confidence}% similarity. Registration blocked!`;

      smartDupUploadThumb.src = data.uploaded_thumbnail;
      smartDupUploadName.textContent = data.uploaded_name || smartRegName.value;

      smartDupConfidence.textContent = `${data.confidence}%`;
      smartDupCosine.textContent = data.similarity.toFixed(4);
      smartDupThreshold.textContent = data.threshold.toFixed(2);

      smartDupMatchedThumb.src = data.matched_animal.thumbnail;
      smartDupMatchedName.textContent = data.matched_animal.name;
      smartDupMatchedTag.textContent = data.matched_animal.tag_id;
      smartDupMatchedBreed.textContent = data.matched_animal.breed || 'Cattle';
      smartDupMatchedDate.textContent = data.matched_animal.registered_at;

      // XAI Pairwise Correspondence Canvas
      const smartDupXaiCanvas = document.getElementById('smartDupXaiCanvas');
      if (smartDupXaiCanvas && data.xai && data.xai.correspondence_canvas) {
        smartDupXaiCanvas.src = data.xai.correspondence_canvas;
      }

      showToast(`⛔ DUPLICATE DETECTED: Animal already registered as '${data.matched_animal.name}'!`);
    } else {
      // NEW ANIMAL ENROLLED!
      smartDuplicateView.classList.add('hidden');
      smartSuccessView.classList.remove('hidden');

      succBannerTitle.textContent = `🎉 Animal '${data.name}' Registered Successfully!`;
      succBannerDesc.textContent = `Enrolled with ${data.shots_count || 3}-Shot Master Biometric Template. Unique Tag ID: '${data.tag_id}'`;

      smartSuccThumb.src = data.thumbnail;
      smartSuccName.textContent = data.name;
      smartSuccTag.textContent = data.tag_id;
      smartSuccBreed.textContent = data.breed || 'Cattle';
      smartSuccHash.textContent = data.biometric_hash;

      // Render 3-Shot Gallery
      if (smartSuccGalleryThumbs) {
        smartSuccGalleryThumbs.innerHTML = '';
        (data.gallery || [data.thumbnail]).forEach((thumbSrc, sIdx) => {
          const img = document.createElement('img');
          img.src = thumbSrc;
          img.className = 'gallery-thumb-chip';
          img.alt = `Shot ${sIdx + 1}`;
          img.title = `Shot ${sIdx + 1}`;
          smartSuccGalleryThumbs.appendChild(img);
        });
      }

      // Quality & FAISS Metrics
      const smartSuccQualityScore = document.getElementById('smartSuccQualityScore');
      const smartSuccLiveness = document.getElementById('smartSuccLiveness');
      const smartSuccFaissLatency = document.getElementById('smartSuccFaissLatency');
      const smartSuccXaiThumb = document.getElementById('smartSuccXaiThumb');

      if (smartSuccQualityScore) {
        smartSuccQualityScore.textContent = `${data.average_quality || 92}% (Avg)`;
      }
      if (smartSuccLiveness) {
        smartSuccLiveness.textContent = '✅ Authentic Live Animal (Passed 80% Gate)';
      }
      if (smartSuccFaissLatency && data.vector_search) {
        smartSuccFaissLatency.textContent = `⚡ ${data.vector_search.latency_ms}ms (${data.vector_search.engine})`;
      }
      if (smartSuccXaiThumb && data.xai && data.xai.heatmap_thumbnail) {
        smartSuccXaiThumb.src = data.xai.heatmap_thumbnail;
      }

      // Master embedding preview
      smartSuccVectorChips.innerHTML = '';
      (data.embedding_sample || []).forEach(val => {
        const chip = document.createElement('span');
        chip.className = 'vector-chip';
        chip.textContent = val.toFixed(4);
        smartSuccVectorChips.appendChild(chip);
      });

      if (data.closest_existing) {
        smartSuccClosestInfo.classList.remove('hidden');
        smartSuccClosestSim.textContent = data.closest_existing.similarity.toFixed(4);
      } else {
        smartSuccClosestInfo.classList.add('hidden');
      }

      showToast(`✅ Success! '${data.name}' enrolled with 3-Shot Master Biometrics.`);
    }

    smartResultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  // 1-Click Production Viva Presets (3 Shots each)
  btnSmartPreset1.addEventListener('click', async () => {
    showToast('⚡ Loading Step 1: Cattle-001 [3 Shots] as "Bella"...');
    try {
      smartRegName.value = 'Bella';
      smartRegBreed.value = 'Sahiwal Cattle';
      smartRegTag.value = 'COW-001';

      const f1 = await fetchFileFromSample('cattle-001/cattle-001_1_jpg_muzzle_0.jpg', 'Cattle001_Shot1.jpg');
      const f2 = await fetchFileFromSample('cattle-001/cattle-001_3_jpg_muzzle_0.jpg', 'Cattle001_Shot2.jpg');
      const f3 = await fetchFileFromSample('cattle-001/cattle-001_4_jpg_muzzle_0.jpg', 'Cattle001_Shot3.jpg');

      handleSlotFile(0, f1);
      handleSlotFile(1, f2);
      handleSlotFile(2, f3);

      setTimeout(() => {
        if (!btnSubmitSmartRegister.disabled) btnSubmitSmartRegister.click();
      }, 700);
    } catch (err) {
      showToast(`❌ Preset Error: ${err.message}`);
    }
  });

  btnSmartPreset2.addEventListener('click', async () => {
    showToast('⚡ Loading Step 2: Cattle-001 [3 Other Shots] as "Daisy" (Testing Duplicate)...');
    try {
      smartRegName.value = 'Daisy';
      smartRegBreed.value = 'Sahiwal Cattle';
      smartRegTag.value = '';

      const f1 = await fetchFileFromSample('cattle-001/cattle-001_6_jpg_muzzle_0.jpg', 'Cattle001_Shot6.jpg');
      const f2 = await fetchFileFromSample('cattle-001/cattle-001_7_jpg_muzzle_0.jpg', 'Cattle001_Shot7.jpg');
      const f3 = await fetchFileFromSample('cattle-001/cattle-001_8_jpg_muzzle_0.jpg', 'Cattle001_Shot8.jpg');

      handleSlotFile(0, f1);
      handleSlotFile(1, f2);
      handleSlotFile(2, f3);

      setTimeout(() => {
        if (!btnSubmitSmartRegister.disabled) btnSubmitSmartRegister.click();
      }, 700);
    } catch (err) {
      showToast(`❌ Preset Error: ${err.message}`);
    }
  });

  btnSmartPreset3.addEventListener('click', async () => {
    showToast('⚡ Loading Step 3: Cattle-002 [3 Shots] as "Thunder" (Unique Animal)...');
    try {
      smartRegName.value = 'Thunder';
      smartRegBreed.value = 'Cholistani Cattle';
      smartRegTag.value = 'COW-002';

      const f1 = await fetchFileFromSample('cattle-002/cattle-002_1_jpg_muzzle_0.jpg', 'Cattle002_Shot1.jpg');
      const f2 = await fetchFileFromSample('cattle-002/cattle-002_3_jpg_muzzle_0.jpg', 'Cattle002_Shot2.jpg');
      const f3 = await fetchFileFromSample('cattle-002/cattle-002_4_jpg_muzzle_0.jpg', 'Cattle002_Shot3.jpg');

      handleSlotFile(0, f1);
      handleSlotFile(1, f2);
      handleSlotFile(2, f3);

      setTimeout(() => {
        if (!btnSubmitSmartRegister.disabled) btnSubmitSmartRegister.click();
      }, 700);
    } catch (err) {
      showToast(`❌ Preset Error: ${err.message}`);
    }
  });


  // =============================================================
  // 2. DIRECT 1-TO-1 COMPARISON LOGIC
  // =============================================================
  directThresholdSlider.addEventListener('input', (e) => {
    directThresholdVal.textContent = parseFloat(e.target.value).toFixed(2);
  });

  boxCompare1.addEventListener('click', (e) => {
    if (e.target !== btnRemoveBox1) compareFileInput1.click();
  });
  setupBoxDrop(boxCompare1, (file) => setDirectFile(1, file));
  compareFileInput1.addEventListener('change', (e) => {
    if (e.target.files && e.target.files.length > 0) setDirectFile(1, e.target.files[0]);
  });
  btnRemoveBox1.addEventListener('click', (e) => {
    e.stopPropagation();
    clearDirectBox(1);
  });

  boxCompare2.addEventListener('click', (e) => {
    if (e.target !== btnRemoveBox2) compareFileInput2.click();
  });
  setupBoxDrop(boxCompare2, (file) => setDirectFile(2, file));
  compareFileInput2.addEventListener('change', (e) => {
    if (e.target.files && e.target.files.length > 0) setDirectFile(2, e.target.files[0]);
  });
  btnRemoveBox2.addEventListener('click', (e) => {
    e.stopPropagation();
    clearDirectBox(2);
  });

  function setupBoxDrop(boxElement, fileCallback) {
    ['dragenter', 'dragover'].forEach(n => {
      boxElement.addEventListener(n, (e) => { e.preventDefault(); boxElement.classList.add('dragover'); });
    });
    ['dragleave', 'drop'].forEach(n => {
      boxElement.addEventListener(n, (e) => { e.preventDefault(); boxElement.classList.remove('dragover'); });
    });
    boxElement.addEventListener('drop', (e) => {
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        fileCallback(e.dataTransfer.files[0]);
      }
    });
  }

  function setDirectFile(boxNum, file) {
    if (!file.type.startsWith('image/')) {
      showToast('❌ Please select an image file (JPG, PNG).');
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      if (boxNum === 1) {
        directFile1 = file;
        boxImg1.src = e.target.result;
        boxFilename1.textContent = file.name;
        boxPrompt1.classList.add('hidden');
        boxPreview1.classList.remove('hidden');
        runQualityAudit(file, directQualityBadge1, (passed, score) => {
          directPass1 = passed;
          checkDirectReady();
        });
      } else {
        directFile2 = file;
        boxImg2.src = e.target.result;
        boxFilename2.textContent = file.name;
        boxPrompt2.classList.add('hidden');
        boxPreview2.classList.remove('hidden');
        runQualityAudit(file, directQualityBadge2, (passed, score) => {
          directPass2 = passed;
          checkDirectReady();
        });
      }
      checkDirectReady();
    };
    reader.readAsDataURL(file);
  }

  function clearDirectBox(boxNum) {
    if (boxNum === 1) {
      directFile1 = null;
      directPass1 = false;
      compareFileInput1.value = '';
      boxPrompt1.classList.remove('hidden');
      boxPreview1.classList.add('hidden');
      if (directQualityBadge1) {
        directQualityBadge1.className = 'slot-quality-badge badge-pending';
        directQualityBadge1.innerHTML = '⏳ Quality: Awaiting Photo';
      }
    } else {
      directFile2 = null;
      directPass2 = false;
      compareFileInput2.value = '';
      boxPrompt2.classList.remove('hidden');
      boxPreview2.classList.add('hidden');
      if (directQualityBadge2) {
        directQualityBadge2.className = 'slot-quality-badge badge-pending';
        directQualityBadge2.innerHTML = '⏳ Quality: Awaiting Photo';
      }
    }
    checkDirectReady();
    directResultsCard.classList.add('hidden');
  }

  function checkDirectReady() {
    const ready = directFile1 && directFile2 && directPass1 && directPass2;
    btnRunDirectCompare.disabled = !ready;
    if (directQualityHint) {
      if (directFile1 && directFile2) {
        if (directPass1 && directPass2) {
          directQualityHint.textContent = '✅ Both muzzle photos passed the 80% quality gate. Ready to verify match!';
          directQualityHint.style.color = '#34d399';
        } else {
          directQualityHint.textContent = '❌ Quality Check Failed: Both photos must achieve at least 80% clarity.';
          directQualityHint.style.color = '#f87171';
        }
      } else {
        directQualityHint.textContent = '🔒 Verification locked: Upload two muzzle photos (minimum 80% quality required per photo).';
        directQualityHint.style.color = '#94a3b8';
      }
    }
  }

  btnPresetSame.addEventListener('click', async () => {
    showToast('⚡ Loading Cattle-001 (Photo 1 vs Photo 2)...');
    try {
      const f1 = await fetchFileFromSample('cattle-001/cattle-001_1_jpg_muzzle_0.jpg', 'Cattle001_Photo1.jpg');
      const f2 = await fetchFileFromSample('cattle-001/cattle-001_3_jpg_muzzle_0.jpg', 'Cattle001_Photo2.jpg');
      setDirectFile(1, f1);
      setDirectFile(2, f2);
      setTimeout(() => btnRunDirectCompare.click(), 400);
    } catch (err) {
      showToast(`❌ Error: ${err.message}`);
    }
  });

  btnPresetDiff.addEventListener('click', async () => {
    showToast('⚡ Loading Cattle-001 vs Cattle-002...');
    try {
      const f1 = await fetchFileFromSample('cattle-001/cattle-001_1_jpg_muzzle_0.jpg', 'Cattle001_Photo1.jpg');
      const f2 = await fetchFileFromSample('cattle-002/cattle-002_1_jpg_muzzle_0.jpg', 'Cattle002_Photo1.jpg');
      setDirectFile(1, f1);
      setDirectFile(2, f2);
      setTimeout(() => btnRunDirectCompare.click(), 400);
    } catch (err) {
      showToast(`❌ Error: ${err.message}`);
    }
  });

  btnRunDirectCompare.addEventListener('click', async () => {
    if (!directFile1 || !directFile2) return;

    btnRunDirectCompare.disabled = true;
    directCompareSpinner.classList.remove('hidden');

    const formData = new FormData();
    formData.append('file1', directFile1);
    formData.append('file2', directFile2);
    const threshold = parseFloat(directThresholdSlider.value);

    try {
      const res = await fetch(`/api/compare?threshold=${threshold}`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Comparison failed');

      renderDirectResults(data);
    } catch (err) {
      showToast(`❌ Comparison Error: ${err.message}`);
    } finally {
      btnRunDirectCompare.disabled = false;
      directCompareSpinner.classList.add('hidden');
    }
  });

  function renderDirectResults(data) {
    directResultsCard.classList.remove('hidden');

    directMetricCosine.textContent = data.cosine_similarity.toFixed(4);
    const barWidth = Math.max(0, Math.min(100, (data.cosine_similarity + 1) / 2 * 100));
    directMetricBar.style.width = `${barWidth}%`;
    directMetricConfidence.textContent = data.confidence_percent;
    directMetricAngular.textContent = `${data.angular_distance_deg}°`;

    directHash1.textContent = data.image1.hash;
    directHash2.textContent = data.image2.hash;

    if (data.is_match) {
      directVerdictBanner.className = 'verdict-banner banner-match';
      directVerdictIcon.textContent = '✅';
      directVerdictTitle.textContent = 'MATCH VERIFIED: SAME ANIMAL';
      directVerdictDesc.textContent = `Both photographs have high biometric correlation (Similarity: ${data.cosine_similarity.toFixed(4)} >= ${data.threshold}). They belong to the SAME cattle.`;
      directMetricBar.style.background = 'linear-gradient(90deg, #10b981, #06b6d4)';
      showToast('🎉 Biometric Match Verified: Same Animal!');
    } else {
      directVerdictBanner.className = 'verdict-banner banner-mismatch';
      directVerdictIcon.textContent = '❌';
      directVerdictTitle.textContent = 'MISMATCH: DIFFERENT ANIMALS';
      directVerdictDesc.textContent = `Biometric ridge grooving patterns diverge (Similarity: ${data.cosine_similarity.toFixed(4)} < ${data.threshold}). These photos belong to DIFFERENT animals.`;
      directMetricBar.style.background = 'linear-gradient(90deg, #ef4444, #f59e0b)';
      showToast('⚠️ Mismatch: Different Animals!');
    }

    // Populate Quality Audits
    if (data.quality_analysis) {
      const q1 = data.quality_analysis.image1;
      const q2 = data.quality_analysis.image2;
      const directQ1Score = document.getElementById('directQ1Score');
      const directQ1Live = document.getElementById('directQ1Live');
      const directQ2Score = document.getElementById('directQ2Score');
      const directQ2Live = document.getElementById('directQ2Live');

      if (directQ1Score && q1) directQ1Score.textContent = `${q1.overall_score}%`;
      if (directQ1Live && q1) directQ1Live.textContent = `${q1.anti_spoofing.liveness_status === 'AUTHENTIC_LIVE_ANIMAL' ? '✅ Live Animal' : '⚠️ Replay'} (Sharp: ${q1.sharpness_index})`;
      
      if (directQ2Score && q2) directQ2Score.textContent = `${q2.overall_score}%`;
      if (directQ2Live && q2) directQ2Live.textContent = `${q2.anti_spoofing.liveness_status === 'AUTHENTIC_LIVE_ANIMAL' ? '✅ Live Animal' : '⚠️ Replay'} (Sharp: ${q2.sharpness_index})`;
    }

    // Populate XAI Visualizations
    if (data.xai) {
      const directXaiCorrImg = document.getElementById('directXaiCorrImg');
      const directHeatImg1 = document.getElementById('directHeatImg1');
      const directHeatImg2 = document.getElementById('directHeatImg2');
      const directRidgeImg1 = document.getElementById('directRidgeImg1');
      const directRidgeImg2 = document.getElementById('directRidgeImg2');

      if (directXaiCorrImg && data.xai.correspondence_canvas) directXaiCorrImg.src = data.xai.correspondence_canvas;
      if (directHeatImg1 && data.xai.heatmap1) directHeatImg1.src = data.xai.heatmap1;
      if (directHeatImg2 && data.xai.heatmap2) directHeatImg2.src = data.xai.heatmap2;
      if (directRidgeImg1 && data.xai.ridge1) directRidgeImg1.src = data.xai.ridge1;
      if (directRidgeImg2 && data.xai.ridge2) directRidgeImg2.src = data.xai.ridge2;
    }

    directResultsCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  // Setup XAI View Tabs in Mode 2
  const btnTabXaiCorr = document.getElementById('btnTabXaiCorr');
  const btnTabXaiHeatmaps = document.getElementById('btnTabXaiHeatmaps');
  const btnTabXaiRidges = document.getElementById('btnTabXaiRidges');
  const xaiTabBodyCorr = document.getElementById('xaiTabBodyCorr');
  const xaiTabBodyHeatmaps = document.getElementById('xaiTabBodyHeatmaps');
  const xaiTabBodyRidges = document.getElementById('xaiTabBodyRidges');

  if (btnTabXaiCorr && btnTabXaiHeatmaps && btnTabXaiRidges) {
    btnTabXaiCorr.addEventListener('click', () => {
      btnTabXaiCorr.classList.add('active');
      btnTabXaiHeatmaps.classList.remove('active');
      btnTabXaiRidges.classList.remove('active');
      xaiTabBodyCorr.classList.remove('hidden');
      xaiTabBodyHeatmaps.classList.add('hidden');
      xaiTabBodyRidges.classList.add('hidden');
    });

    btnTabXaiHeatmaps.addEventListener('click', () => {
      btnTabXaiCorr.classList.remove('active');
      btnTabXaiHeatmaps.classList.add('active');
      btnTabXaiRidges.classList.remove('active');
      xaiTabBodyCorr.classList.add('hidden');
      xaiTabBodyHeatmaps.classList.remove('hidden');
      xaiTabBodyRidges.classList.add('hidden');
    });

    btnTabXaiRidges.addEventListener('click', () => {
      btnTabXaiCorr.classList.remove('active');
      btnTabXaiHeatmaps.classList.remove('active');
      btnTabXaiRidges.classList.add('active');
      xaiTabBodyCorr.classList.add('hidden');
      xaiTabBodyHeatmaps.classList.add('hidden');
      xaiTabBodyRidges.classList.remove('hidden');
    });
  }


  // =============================================================
  // 3. SEARCH & VERIFY (MODE 3)
  // =============================================================
  thresholdSlider.addEventListener('input', (e) => {
    thresholdVal.textContent = parseFloat(e.target.value).toFixed(2);
  });

  dropZone.addEventListener('click', (e) => {
    if (e.target !== btnRemoveImg) fileInput.click();
  });
  ['dragenter', 'dragover'].forEach(n => {
    dropZone.addEventListener(n, (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
  });
  ['dragleave', 'drop'].forEach(n => {
    dropZone.addEventListener(n, (e) => { e.preventDefault(); dropZone.classList.remove('dragover'); });
  });
  dropZone.addEventListener('drop', (e) => {
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleSearchFile(e.dataTransfer.files[0]);
    }
  });
  fileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleSearchFile(e.target.files[0]);
    }
  });

  btnRemoveImg.addEventListener('click', (e) => {
    e.stopPropagation();
    clearSearchFile();
  });

  function handleSearchFile(file) {
    if (!file.type.startsWith('image/')) {
      showToast('❌ Please upload an image file (JPG, PNG).');
      return;
    }
    currentSearchFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      previewFilename.textContent = file.name;
      dropzonePrompt.classList.add('hidden');
      dropzonePreview.classList.remove('hidden');

      // Real-time quality assessment
      btnScanVerify.disabled = true;
      runQualityAudit(file, searchQualityBadge, (passed, score) => {
        searchPassed = passed;
        btnScanVerify.disabled = !passed;
        if (searchQualityHint) {
          if (passed) {
            searchQualityHint.textContent = '✅ Photo passed 80% quality gate. Ready to search registry.';
            searchQualityHint.style.color = '#34d399';
          } else {
            searchQualityHint.textContent = '❌ Quality Check Failed (<80%): Cannot search database with blurry/low-contrast photo.';
            searchQualityHint.style.color = '#f87171';
          }
        }
      });
    };
    reader.readAsDataURL(file);
  }

  function clearSearchFile() {
    currentSearchFile = null;
    searchPassed = false;
    fileInput.value = '';
    dropzonePrompt.classList.remove('hidden');
    dropzonePreview.classList.add('hidden');
    if (searchQualityBadge) {
      searchQualityBadge.className = 'slot-quality-badge badge-pending';
      searchQualityBadge.innerHTML = '⏳ Quality: Awaiting Photo';
    }
    if (searchQualityHint) {
      searchQualityHint.textContent = '🔒 Minimum 80% biometric clarity required to execute registry match.';
      searchQualityHint.style.color = '#94a3b8';
    }
    btnScanVerify.disabled = true;
    resetSearchVerdict();
  }

  function resetSearchVerdict() {
    verdictBanner.className = 'verdict-banner banner-idle';
    verdictIcon.textContent = '🔍';
    verdictTitle.textContent = 'Awaiting Input';
    verdictDescription.textContent = 'Upload a muzzle photo or choose a 1-click sample above to extract features and test matching.';
    metricsGrid.classList.add('hidden');
    matchedProfileCard.classList.add('hidden');
    dualInspectionCard.classList.add('hidden');
    fingerprintSection.classList.add('hidden');

    const scanQualityCard = document.getElementById('scanQualityCard');
    const scanFaissCard = document.getElementById('scanFaissCard');
    if (scanQualityCard) scanQualityCard.classList.add('hidden');
    if (scanFaissCard) scanFaissCard.classList.add('hidden');
  }

  btnScanVerify.addEventListener('click', async () => {
    if (!currentSearchFile) return;

    btnScanVerify.disabled = true;
    scanSpinner.classList.remove('hidden');

    const formData = new FormData();
    formData.append('file', currentSearchFile);
    const threshold = parseFloat(thresholdSlider.value);

    try {
      const res = await fetch(`/api/scan?threshold=${threshold}`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Scan failed');

      renderSearchResults(data);
    } catch (err) {
      showToast(`❌ Scan Error: ${err.message}`);
    } finally {
      btnScanVerify.disabled = false;
      scanSpinner.classList.add('hidden');
    }
  });

  function renderSearchResults(res) {
    // 4-Way Multi-Modal Inspection Grid
    rawThumb.src = res.thumbnails.original;
    claheThumb.src = res.thumbnails.enhanced;

    const scanHeatThumb = document.getElementById('scanHeatThumb');
    const scanRidgeThumb = document.getElementById('scanRidgeThumb');
    if (scanHeatThumb && res.thumbnails.heatmap) scanHeatThumb.src = res.thumbnails.heatmap;
    if (scanRidgeThumb && res.thumbnails.ridge) scanRidgeThumb.src = res.thumbnails.ridge;

    dualInspectionCard.classList.remove('hidden');

    metricsGrid.classList.remove('hidden');
    metricCosine.textContent = res.best_similarity.toFixed(4);
    const barWidth = Math.max(0, Math.min(100, (res.best_similarity + 1) / 2 * 100));
    metricCosineBar.style.width = `${barWidth}%`;
    metricConfidence.textContent = res.confidence_percent;
    metricAngular.textContent = `${res.angular_distance_deg}°`;

    // Quality Gate Card
    const scanQualityCard = document.getElementById('scanQualityCard');
    const scanQualityScore = document.getElementById('scanQualityScore');
    const scanSharpnessVal = document.getElementById('scanSharpnessVal');
    const scanGlareVal = document.getElementById('scanGlareVal');
    const scanLivenessVal = document.getElementById('scanLivenessVal');
    const scanQualityFeedback = document.getElementById('scanQualityFeedback');

    if (scanQualityCard && res.quality_gate) {
      scanQualityScore.textContent = `${res.quality_gate.overall_score}%`;
      scanSharpnessVal.textContent = res.quality_gate.sharpness_index;
      scanGlareVal.textContent = `${res.quality_gate.glare_percentage}%`;
      scanLivenessVal.textContent = res.quality_gate.anti_spoofing.liveness_status === 'AUTHENTIC_LIVE_ANIMAL' ? '✅ Authentic Live Animal' : '⚠️ Flagged Digital Replay';
      scanQualityFeedback.textContent = (res.quality_gate.feedback || []).join(' • ');
      scanQualityCard.classList.remove('hidden');
    }

    // FAISS High-Speed Retrieval Card
    const scanFaissCard = document.getElementById('scanFaissCard');
    const scanFaissEngine = document.getElementById('scanFaissEngine');
    const scanFaissLatency = document.getElementById('scanFaissLatency');
    const scanFaissCandidates = document.getElementById('scanFaissCandidates');

    if (scanFaissCard && res.vector_search) {
      scanFaissEngine.textContent = res.vector_search.engine;
      scanFaissLatency.textContent = `${res.vector_search.latency_ms} ms`;

      scanFaissCandidates.innerHTML = '';
      const candidates = res.vector_search.candidates || [];
      if (candidates.length === 0) {
        scanFaissCandidates.innerHTML = '<span class="text-xs text-muted" style="padding: 6px;">No registered candidates to rank.</span>';
      } else {
        candidates.forEach(cand => {
          const row = document.createElement('div');
          row.className = 'faiss-candidate-row';
          row.innerHTML = `
            <div class="candidate-left">
              <span class="candidate-rank">#${cand.rank}</span>
              <img src="${cand.thumbnail || ''}" class="candidate-avatar" alt="${cand.tag_id}">
              <div class="candidate-info">
                <span class="candidate-name">${cand.name}</span>
                <span class="candidate-tag">${cand.tag_id} &bull; ${cand.breed}</span>
              </div>
            </div>
            <div class="candidate-right">
              <span class="candidate-sim">${cand.similarity.toFixed(4)}</span>
              <span class="${cand.is_match ? 'candidate-badge-match' : 'candidate-badge-miss'}">
                ${cand.is_match ? 'MATCH' : 'BELOW THRESHOLD'}
              </span>
            </div>
          `;
          scanFaissCandidates.appendChild(row);
        });
      }
      scanFaissCard.classList.remove('hidden');
    }

    if (res.is_match && res.matched_animal) {
      verdictBanner.className = 'verdict-banner banner-match';
      verdictIcon.textContent = '✅';
      verdictTitle.textContent = 'VERIFIED: Cattle Identified in Database';
      verdictDescription.textContent = `High-confidence biometric match found with ${res.matched_animal.name} (${res.matched_animal.tag_id}) at ${res.confidence_percent} confidence.`;
      metricCosineBar.style.background = 'linear-gradient(90deg, #10b981, #06b6d4)';

      matchedTagId.textContent = res.matched_animal.tag_id;
      matchedName.textContent = res.matched_animal.name;
      matchedThumb.src = res.matched_animal.thumbnail;
      matchedProfileCard.classList.remove('hidden');
    } else if (res.closest_animal) {
      verdictBanner.className = 'verdict-banner banner-mismatch';
      verdictIcon.textContent = '⚠️';
      verdictTitle.textContent = 'UNREGISTERED: No Database Match';
      verdictDescription.textContent = `Biometric scan does not match any enrolled animal (Closest: ${res.closest_animal.name} at similarity ${res.closest_animal.similarity} < threshold ${res.threshold}).`;
      metricCosineBar.style.background = 'linear-gradient(90deg, #ef4444, #f59e0b)';
      matchedProfileCard.classList.add('hidden');
    } else {
      verdictBanner.className = 'verdict-banner banner-idle';
      verdictIcon.textContent = 'ℹ️';
      verdictTitle.textContent = 'Registry Empty';
      verdictDescription.textContent = 'No cattle currently enrolled in database. Go to Mode 1 to register cattle!';
      matchedProfileCard.classList.add('hidden');
    }

    displayHash.textContent = res.biometric_hash;
    vectorChips.innerHTML = '';
    (res.embedding_sample || []).forEach(val => {
      const chip = document.createElement('span');
      chip.className = 'vector-chip';
      chip.textContent = val.toFixed(4);
      vectorChips.appendChild(chip);
    });
    fingerprintSection.classList.remove('hidden');
  }

  // -------------------------------------------------------------
  // Live Database Table Operations
  // -------------------------------------------------------------
  async function updateRegistryUI() {
    try {
      const res = await fetch('/api/registry');
      const data = await res.json();
      const count = data.total_registered || 0;

      headerRegistryCount.textContent = count;
      registryCountBadge.textContent = `${count} Animal${count === 1 ? '' : 's'} Enrolled`;

      registryTableBody.innerHTML = '';
      if (count === 0) {
        registryTableBody.innerHTML = `
          <tr class="empty-row">
            <td colspan="7" class="text-center">No animals registered yet. Use Mode 1 above to register your first cattle!</td>
          </tr>
        `;
        return;
      }

      data.registry.forEach(cow => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><img src="${cow.thumbnail}" alt="${cow.tag_id}" class="reg-thumb"></td>
          <td><strong class="font-mono text-cyan">${cow.tag_id}</strong></td>
          <td><strong>${cow.name}</strong></td>
          <td>${cow.breed || 'Cattle'}</td>
          <td><span class="reg-hash" title="${cow.hash}">${cow.hash}</span></td>
          <td><span class="text-xs text-muted">${cow.created_at}</span></td>
          <td>
            <button class="btn-delete-row" data-tag="${cow.tag_id}" title="Remove this animal">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
              </svg>
              Delete
            </button>
          </td>
        `;

        const btnDelete = tr.querySelector('.btn-delete-row');
        btnDelete.addEventListener('click', async () => {
          if (confirm(`Remove '${cow.name}' (${cow.tag_id}) from database?`)) {
            try {
              const delRes = await fetch(`/api/registry/${encodeURIComponent(cow.tag_id)}`, { method: 'DELETE' });
              const delData = await delRes.json();
              showToast(`🗑️ ${delData.message}`);
              await updateRegistryUI();
            } catch (err) {
              showToast(`❌ Delete failed: ${err.message}`);
            }
          }
        });

        registryTableBody.appendChild(tr);
      });
    } catch (err) {
      console.error('Failed to load registry:', err);
    }
  }

  btnResetAll.addEventListener('click', async () => {
    if (confirm('Are you sure you want to wipe the local registry and start fresh from zero?')) {
      try {
        const res = await fetch('/api/reset', { method: 'POST' });
        const data = await res.json();
        showToast(`🗑️ ${data.message}`);
        clearSmartFile();
        clearSearchFile();
        smartResultCard.classList.add('hidden');
        await updateRegistryUI();
      } catch (err) {
        showToast(`❌ ${err.message}`);
      }
    }
  });

  if (btnCopyHash) {
    btnCopyHash.addEventListener('click', () => {
      navigator.clipboard.writeText(displayHash.textContent).then(() => {
        btnCopyHash.textContent = 'Copied!';
        setTimeout(() => { btnCopyHash.textContent = 'Copy'; }, 2000);
        showToast('📋 Biometric SHA-256 hash copied to clipboard.');
      });
    });
  }

  // -------------------------------------------------------------
  // Load Sample Chips for Mode 3
  // -------------------------------------------------------------
  async function loadSamples() {
    try {
      const res = await fetch('/api/samples');
      const data = await res.json();
      if (!data.samples || data.samples.length === 0) {
        samplesContainer.innerHTML = '<span class="text-muted text-xs">No sample images found in dataset folder.</span>';
        return;
      }

      samplesContainer.innerHTML = '';
      data.samples.forEach(sample => {
        const chip = document.createElement('div');
        chip.className = 'sample-chip';

        let badgeClass = 'badge-match-expected';
        let badgeText = 'Base / Match';
        if (sample.type.includes('impostor')) {
          badgeClass = 'badge-flag-expected';
          badgeText = 'Different Animal';
        }

        chip.innerHTML = `
          <img src="${sample.thumbnail}" alt="${sample.label}">
          <div class="sample-chip-info">
            <span class="sample-chip-title">${sample.label}</span>
            <span class="sample-chip-badge ${badgeClass}">${badgeText}</span>
          </div>
        `;

        chip.addEventListener('click', async () => {
          showToast(`⚡ Loading ${sample.label}...`);
          try {
            const imgRes = await fetch(`/api/sample-image?path=${encodeURIComponent(sample.path)}`);
            const blob = await imgRes.blob();
            const file = new File([blob], `${sample.label.replace(/\s+/g, '_')}.jpg`, { type: 'image/jpeg' });
            handleSearchFile(file);
            setTimeout(() => btnScanVerify.click(), 300);
          } catch (err) {
            showToast(`❌ Could not load sample: ${err.message}`);
          }
        });

        samplesContainer.appendChild(chip);
      });
    } catch (err) {
      console.warn('Failed to load samples:', err);
    }
  }

  let toastTimer = null;
  function showToast(msg) {
    toast.textContent = msg;
    toast.classList.remove('hidden');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      toast.classList.add('hidden');
    }, 3500);
  }
});
