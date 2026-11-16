/* CyberEye Build 2: screenshot-to-text OCR, performed locally in the browser.
 * The selected image is never POSTed to the CyberEye server or OpenRouter.
 * Text is only sent to OpenRouter when the user clicks Analyze message.
 */
(() => {
  'use strict';
  const OCR_SCRIPT_URL = 'https://cdn.jsdelivr.net/npm/tesseract.js@7.0.0/dist/tesseract.min.js';
  const MAX_IMAGE_BYTES = 10 * 1024 * 1024;
  const ALLOWED_TYPES = new Set(['image/png', 'image/jpeg', 'image/webp', 'image/bmp']);
  const MAX_ANALYSIS_CHARS = 5000;

  const uploadButton = document.getElementById('upload-screenshot');
  const fileInput = document.getElementById('screenshot-file');
  const textInput = document.getElementById('message');
  const analyzeButton = document.getElementById('analyze');
  const status = document.getElementById('ocr-status');
  if (!uploadButton || !fileInput || !textInput || !analyzeButton || !status) return;

  let loadingPromise = null;
  let isScanning = false;
  function setStatus(message, isError = false) {
    status.textContent = message;
    status.classList.toggle('error-text', isError);
  }
  function loadOCR() {
    if (window.Tesseract && typeof window.Tesseract.createWorker === 'function') {
      return Promise.resolve(window.Tesseract);
    }
    if (!loadingPromise) {
      loadingPromise = new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = OCR_SCRIPT_URL;
        script.async = true;
        script.crossOrigin = 'anonymous';
        script.onload = () => {
          if (window.Tesseract && typeof window.Tesseract.createWorker === 'function') {
            resolve(window.Tesseract);
          } else {
            reject(new Error('OCR script did not load correctly'));
          }
        };
        script.onerror = () => reject(new Error('OCR library could not be downloaded'));
        document.head.appendChild(script);
      }).catch((error) => {
        loadingPromise = null;
        throw error;
      });
    }
    return loadingPromise;
  }

  uploadButton.addEventListener('click', () => {
    if (!isScanning && !analyzeButton.disabled) fileInput.click();
  });

  fileInput.addEventListener('change', async () => {
    const file = fileInput.files && fileInput.files[0];
    fileInput.value = ''; // Allow selecting the same file again.
    if (!file || isScanning) return;
    if (analyzeButton.disabled) {
      setStatus('Finish the current analysis before uploading another screenshot.', true);
      return;
    }
    if (!ALLOWED_TYPES.has(file.type)) {
      setStatus('Please choose a PNG, JPG, WebP, or BMP image.', true);
      return;
    }
    if (!file.size || file.size > MAX_IMAGE_BYTES) {
      setStatus('Please choose an image smaller than 10 MB.', true);
      return;
    }

    isScanning = true;
    uploadButton.disabled = true;
    analyzeButton.disabled = true;
    uploadButton.textContent = 'Scanning screenshot…';
    setStatus('Loading on-device text recognition. The first scan may download language files.');
    window.posthog?.capture('screenshot_ocr_started', { source: 'local_app' });

    let worker = null;
    try {
      const Tesseract = await loadOCR();
      worker = await Tesseract.createWorker('eng', 1, {
        logger: (event) => {
          if (event.status === 'recognizing text' && typeof event.progress === 'number') {
            setStatus('Reading screenshot text… ' + Math.round(event.progress * 100) + '%');
          }
        }
      });
      const response = await worker.recognize(file);
      const extracted = (response && response.data && response.data.text || '').trim();

      if (!extracted) {
        setStatus('No readable text was found. Try a clearer screenshot with larger text.', true);
        window.posthog?.capture('screenshot_ocr_failed', { source: 'local_app', reason: 'empty' });
        return;
      }
      // A successful scan replaces the textarea; the user can edit before sending.
      textInput.value = extracted;
      textInput.scrollTop = 0;
      textInput.focus();
      setStatus(extracted.length > MAX_ANALYSIS_CHARS
        ? 'Text extracted, but it exceeds 5,000 characters. Shorten it before analyzing.'
        : 'Text extracted. Review and correct it below, then click Analyze message.');
      window.posthog?.capture('screenshot_ocr_completed', {
        source: 'local_app', characters: extracted.length
      });
    } catch (error) {
      setStatus('Could not read this screenshot. Check your connection and try a clearer PNG or JPG.', true);
      window.posthog?.capture('screenshot_ocr_failed', { source: 'local_app', reason: 'processing' });
    } finally {
      if (worker) {
        try { await worker.terminate(); } catch (_) { /* release attempted */ }
      }
      isScanning = false;
      uploadButton.disabled = false;
      analyzeButton.disabled = false;
      uploadButton.textContent = 'Upload screenshot';
    }
  });
})();
