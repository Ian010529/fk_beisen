const statusElement = document.getElementById('status');
const identifyButton = document.getElementById('identify');

async function refreshStatus() {
  const response = await chrome.runtime.sendMessage({ action: 'checkService' });
  if (response?.ok) {
    const data = response.data;
    statusElement.textContent = `服务正常：${data.questions} 题，${data.images} 张索引图`;
    identifyButton.disabled = false;
  } else {
    statusElement.textContent = response?.error || '本地服务不可用';
    identifyButton.disabled = true;
  }
}

identifyButton.addEventListener('click', async () => {
  identifyButton.disabled = true;
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id) return;
  try {
    await chrome.tabs.sendMessage(tab.id, { action: 'identifyCurrent' });
    window.close();
  } catch (error) {
    statusElement.textContent = '当前页面没有加载识别脚本';
    identifyButton.disabled = false;
  }
});

refreshStatus();
