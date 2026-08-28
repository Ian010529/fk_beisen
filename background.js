const MATCHER_URL = 'http://127.0.0.1:8765';

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'checkService') {
    checkService().then(sendResponse);
    return true;
  }
  if (request.action === 'matchQuestion') {
    matchQuestion(request.payload || {}, sender.tab?.windowId).then(sendResponse);
    return true;
  }
  if (request.action === 'captureVisiblePage') {
    captureVisiblePage(sender.tab?.windowId).then(sendResponse);
    return true;
  }
});

async function checkService() {
  try {
    const response = await fetch(`${MATCHER_URL}/health`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return { ok: true, data: await response.json() };
  } catch (error) {
    return { ok: false, error: `本地识别服务未启动：${error.message}` };
  }
}

async function matchQuestion(payload, windowId) {
  try {
    const images = await Promise.all((payload.imageUrls || []).slice(0, 6).map(fetchImage));
    const usableImages = images.filter(Boolean);
    let captureError = '';
    if (
      payload.useCodex === true && payload.hasVisual === true &&
      usableImages.length === 0 && payload.captureAttempted !== true
    ) {
      const capture = await captureVisiblePage(windowId);
      if (capture.ok) usableImages.push({ data: capture.data });
      else captureError = capture.error;
    }
    const response = await fetch(`${MATCHER_URL}/match`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        stem: payload.stem || '',
        options: payload.options || [],
        images: usableImages,
        use_codex: payload.useCodex === true
      })
    });
    if (!response.ok) {
      const detail = await response.json().catch(() => null);
      throw new Error(detail?.error || `识别服务返回 HTTP ${response.status}`);
    }
    const data = await response.json();
    if (captureError && data?.match) data.match.capture_error = captureError;
    return { ok: true, data };
  } catch (error) {
    return { ok: false, error: error.message };
  }
}

async function captureVisiblePage(windowId) {
  if (!Number.isInteger(windowId)) {
    return { ok: false, error: '无法确定当前测评窗口' };
  }
  try {
    const data = await chrome.tabs.captureVisibleTab(windowId, { format: 'jpeg', quality: 90 });
    return data
      ? { ok: true, data }
      : { ok: false, error: '当前页面截图为空' };
  } catch (_) {
    return {
      ok: false,
      error: '截图未授权：进入测评前请点击一次浏览器工具栏中的扩展图标'
    };
  }
}

async function fetchImage(url) {
  if (!url) return null;
  if (url.startsWith('data:')) return { data: url };
  try {
    const response = await fetch(url, { credentials: 'include' });
    if (!response.ok) return null;
    const blob = await response.blob();
    const supported = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
    if (!supported.includes(blob.type) || blob.size > 8 * 1024 * 1024) return null;
    return { data: await blobToDataUrl(blob) };
  } catch (_) {
    return null;
  }
}

async function blobToDataUrl(blob) {
  const bytes = new Uint8Array(await blob.arrayBuffer());
  let binary = '';
  for (let offset = 0; offset < bytes.length; offset += 32768) {
    binary += String.fromCharCode(...bytes.subarray(offset, offset + 32768));
  }
  return `data:${blob.type};base64,${btoa(binary)}`;
}
