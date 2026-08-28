const MATCHER_URL = 'http://127.0.0.1:8765';

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'checkService') {
    checkService().then(sendResponse);
    return true;
  }
  if (request.action === 'matchQuestion') {
    matchQuestion(request.payload || {}).then(sendResponse);
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

async function matchQuestion(payload) {
  try {
    const images = await Promise.all((payload.imageUrls || []).slice(0, 6).map(fetchImage));
    const response = await fetch(`${MATCHER_URL}/match`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        stem: payload.stem || '',
        options: payload.options || [],
        images: images.filter(Boolean),
        use_codex: payload.useCodex === true
      })
    });
    if (!response.ok) throw new Error(`识别服务返回 HTTP ${response.status}`);
    return { ok: true, data: await response.json() };
  } catch (error) {
    return { ok: false, error: error.message };
  }
}

async function fetchImage(url) {
  if (!url) return null;
  if (url.startsWith('data:')) return { data: url };
  try {
    const response = await fetch(url, { credentials: 'include' });
    if (!response.ok) return null;
    const blob = await response.blob();
    if (!blob.type.startsWith('image/') || blob.size > 8 * 1024 * 1024) return null;
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
