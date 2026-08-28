(() => {
  'use strict';

  const platformKey = location.hostname === 'iflytek.ceping.com' ? 'iflytek' : 'beisen';
  const config = window.PLATFORM_CONFIG[platformKey];
  let currentOptionElements = [];
  let autoRecognize = true;
  let personalityStrategy = 'profile';
  let identifyInFlight = false;
  let lastFingerprint = '';
  let recognizeTimer = null;

  function isVisible(element) {
    const rect = element.getBoundingClientRect();
    const style = getComputedStyle(element);
    return rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
  }

  function textOf(element) {
    return (element?.innerText || element?.textContent || '').replace(/\s+/g, ' ').trim();
  }

  function findQuestion() {
    for (const selector of config.selectors.question) {
      const candidates = [...document.querySelectorAll(selector)].filter(isVisible);
      if (candidates.length) {
        return candidates.sort((a, b) => b.getBoundingClientRect().height - a.getBoundingClientRect().height)[0];
      }
    }
    return null;
  }

  function findStem(question) {
    for (const selector of config.selectors.stem) {
      const element = [...question.querySelectorAll(selector)].find(isVisible);
      const value = textOf(element);
      if (value.length >= 4) return value;
    }
    return '';
  }

  function findOptions(question) {
    for (const selector of config.selectors.options) {
      const elements = [...question.querySelectorAll(selector)].filter(isVisible);
      const usable = elements.filter(element => textOf(element).length > 0);
      if (usable.length >= 2 && usable.length <= 8) return usable;
    }
    return [];
  }

  function extractCurrentQuestion() {
    const question = findQuestion();
    if (!question) throw new Error('没有检测到当前题目容器');
    currentOptionElements = findOptions(question);
    if (currentOptionElements.length < 2) throw new Error('没有检测到可匹配的选项');
    const imageUrls = [...question.querySelectorAll('img')]
      .filter(image => isVisible(image) && image.naturalWidth >= 40 && image.naturalHeight >= 40)
      .map(image => image.currentSrc || image.src)
      .filter(Boolean);
    return {
      stem: findStem(question),
      options: currentOptionElements.map(textOf),
      imageUrls
    };
  }

  function fingerprint(payload) {
    return JSON.stringify([payload.stem, payload.options, payload.imageUrls]);
  }

  function isPersonalityScale(options) {
    const scaleWords = [
      '符合', '不符合', '同意', '不同意', '愿意', '不愿意',
      '总是', '经常', '有时', '偶尔', '从不', '非常像', '不像'
    ];
    return options.filter(option => scaleWords.some(word => option.includes(word))).length >= 2;
  }

  function normalizeProfileText(value) {
    return value.replace(/[\s，。！？、；：,.!?;:()（）]/g, '');
  }

  function findProfileAnswer(stem) {
    const needle = normalizeProfileText(stem);
    for (const [answer, questions] of Object.entries(window.PSYCHOMETRIC_PROFILE.answerCategories)) {
      for (const question of questions) {
        const candidate = normalizeProfileText(question);
        if (needle.includes(candidate) || candidate.includes(needle)) return answer;
      }
    }
    return window.PSYCHOMETRIC_PROFILE.defaultAnswer;
  }

  function selectPersonalityOption(stem, options) {
    if (personalityStrategy === 'profile') {
      const answer = findProfileAnswer(stem);
      const index = options.findIndex(option => normalizeProfileText(option).includes(answer));
      return index >= 0 ? index : 0;
    }
    if (personalityStrategy === 'random') {
      return Math.floor(Math.random() * options.length);
    }
    if (personalityStrategy === 'positive') {
      return Math.min(Math.floor(options.length * 0.6), options.length - 1);
    }

    const positiveWords = ['团队', '合作', '学习', '成长', '积极', '主动', '创新', '沟通', '协调'];
    const negativeWords = ['冲突', '困难', '压力', '挑战', '失败', '矛盾', '问题'];
    const positive = positiveWords.some(word => stem.includes(word));
    const negative = negativeWords.some(word => stem.includes(word));
    if (positive && !negative) return Math.min(1, options.length - 1);
    return Math.floor(options.length / 2);
  }

  function showPersonalitySuggestion(payload) {
    const index = selectPersonalityOption(payload.stem, payload.options);
    if (currentOptionElements[index]) {
      currentOptionElements[index].classList.add('beisen-helper-answer');
    }
    const strategyNames = { profile: '题库', positive: '积极', balanced: '平衡', random: '随机' };
    setStatus(
      `心理测评 · ${strategyNames[personalityStrategy]}策略<br><strong>${escapeHtml(payload.options[index])}</strong>`,
      'success',
      true
    );
  }

  function isAdjectiveChoice(options) {
    return options.length === 3 && Boolean(document.querySelector('[data-cls="tuozhuai-content"]'));
  }

  function showAdjectiveSuggestion(payload) {
    const ranking = window.PSYCHOMETRIC_PROFILE.adjectiveRanking;
    const ranked = payload.options.map((option, index) => {
      const priority = ranking.findIndex(adjective => option.includes(adjective));
      return { index, priority: priority >= 0 ? priority : ranking.length };
    }).sort((a, b) => a.priority - b.priority);
    const most = ranked[0].index;
    const least = ranked[ranked.length - 1].index;
    currentOptionElements[most]?.classList.add('beisen-helper-most');
    currentOptionElements[least]?.classList.add('beisen-helper-least');
    setStatus(
      `形容词三选二<br><strong>最符合：${escapeHtml(payload.options[most])}</strong><br>` +
      `最不符合：${escapeHtml(payload.options[least])}`,
      'success',
      true
    );
  }

  async function identify({ automatic = false } = {}) {
    if (identifyInFlight) return;
    let payload;
    try {
      payload = extractCurrentQuestion();
    } catch (error) {
      if (!automatic) setStatus(error.message, 'error');
      return;
    }
    const currentFingerprint = fingerprint(payload);
    if (automatic && (!autoRecognize || currentFingerprint === lastFingerprint)) return;

    identifyInFlight = true;
    setStatus('正在识别…', 'working');
    clearHighlights();
    try {
      if (isAdjectiveChoice(payload.options)) {
        lastFingerprint = currentFingerprint;
        showAdjectiveSuggestion(payload);
        return;
      }
      if (isPersonalityScale(payload.options)) {
        lastFingerprint = currentFingerprint;
        showPersonalitySuggestion(payload);
        return;
      }
      const response = await chrome.runtime.sendMessage({ action: 'matchQuestion', payload });
      if (!response?.ok) throw new Error(response?.error || '识别请求失败');
      const match = response.data?.match;
      if (!match) throw new Error('题库中没有达到阈值的候选题');
      lastFingerprint = currentFingerprint;
      showMatch(match);
    } catch (error) {
      setStatus(error.message, 'error');
    } finally {
      identifyInFlight = false;
    }
  }

  function scheduleAutoRecognize() {
    clearTimeout(recognizeTimer);
    recognizeTimer = setTimeout(() => {
      if (!findQuestion()) return;
      createPanel();
      identify({ automatic: true });
    }, 500);
  }

  function placePanelForFullscreen() {
    const panel = document.getElementById('beisen-helper-panel');
    if (!panel) return;
    const fullscreen = document.fullscreenElement;
    const replacedElement = fullscreen?.matches('iframe, object, embed');
    const host = fullscreen && !replacedElement ? fullscreen : document.body;
    if (host && panel.parentElement !== host) host.appendChild(panel);
  }

  function showMatch(match) {
    const index = match.page_option_index;
    if (Number.isInteger(index) && currentOptionElements[index]) {
      currentOptionElements[index].classList.add('beisen-helper-answer');
    }
    const confidence = Math.round((match.confidence || 0) * 100);
    const optionConfidence = Math.round((match.option_confidence || 0) * 100);
    const answer = match.page_option_text || `${match.answer_key}. ${match.answer_text}`;
    setStatus(
      `${match.question_id} · ${match.method} ${confidence}%<br><strong>${escapeHtml(answer)}</strong><br>选项匹配 ${optionConfidence}%`,
      'success',
      true
    );
  }

  function clearHighlights() {
    document.querySelectorAll('.beisen-helper-answer, .beisen-helper-most, .beisen-helper-least').forEach(element => {
      element.classList.remove('beisen-helper-answer', 'beisen-helper-most', 'beisen-helper-least');
    });
  }

  function setStatus(message, kind = '', html = false) {
    const element = document.getElementById('beisen-helper-status');
    if (!element) return;
    element.className = kind;
    if (html) element.innerHTML = message;
    else element.textContent = message;
  }

  function escapeHtml(value) {
    const element = document.createElement('div');
    element.textContent = value;
    return element.innerHTML;
  }

  function createPanel() {
    if (document.getElementById('beisen-helper-panel')) return;
    const panel = document.createElement('aside');
    panel.id = 'beisen-helper-panel';
    panel.innerHTML = `
      <div class="beisen-helper-header">
        <strong>北森题库识别</strong>
        <button id="beisen-helper-toggle" title="收起">−</button>
      </div>
      <div id="beisen-helper-body">
        <button id="beisen-helper-identify">识别当前题</button>
        <div class="beisen-helper-shortcut">全屏快捷键：Alt/⌥ + Shift + B</div>
        <label class="beisen-helper-auto">
          <input id="beisen-helper-auto" type="checkbox" ${autoRecognize ? 'checked' : ''}>
          自动识别新题
        </label>
        <label class="beisen-helper-strategy">
          心理策略
          <select id="beisen-helper-strategy">
            <option value="profile" ${personalityStrategy === 'profile' ? 'selected' : ''}>题库</option>
            <option value="positive" ${personalityStrategy === 'positive' ? 'selected' : ''}>积极</option>
            <option value="balanced" ${personalityStrategy === 'balanced' ? 'selected' : ''}>平衡</option>
            <option value="random" ${personalityStrategy === 'random' ? 'selected' : ''}>随机</option>
          </select>
        </label>
        <div id="beisen-helper-status">等待识别</div>
      </div>`;
    document.body.appendChild(panel);
    placePanelForFullscreen();
    document.getElementById('beisen-helper-identify').addEventListener('click', identify);
    document.getElementById('beisen-helper-auto').addEventListener('change', event => {
      autoRecognize = event.currentTarget.checked;
      chrome.storage.local.set({ autoRecognize });
      if (autoRecognize) {
        lastFingerprint = '';
        scheduleAutoRecognize();
      }
    });
    document.getElementById('beisen-helper-strategy').addEventListener('change', event => {
      personalityStrategy = event.currentTarget.value;
      chrome.storage.local.set({ personalityStrategy });
      lastFingerprint = '';
      scheduleAutoRecognize();
    });
    document.getElementById('beisen-helper-toggle').addEventListener('click', event => {
      const body = document.getElementById('beisen-helper-body');
      const hidden = body.hidden;
      body.hidden = !hidden;
      event.currentTarget.textContent = hidden ? '−' : '+';
    });
  }

  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'identifyCurrent') {
      identify().then(() => sendResponse({ ok: true }));
      return true;
    }
  });

  function init() {
    chrome.storage.local.get({ autoRecognize: true, personalityStrategy: 'profile' }, result => {
      autoRecognize = result.autoRecognize !== false;
      personalityStrategy = result.personalityStrategy || 'profile';
      if (window === window.top || findQuestion()) createPanel();

      const observer = new MutationObserver(mutations => {
        const onlyPanelChanges = mutations.every(mutation => {
          const target = mutation.target.nodeType === Node.ELEMENT_NODE
            ? mutation.target
            : mutation.target.parentElement;
          return target?.closest?.('#beisen-helper-panel');
        });
        if (!onlyPanelChanges) scheduleAutoRecognize();
      });
      observer.observe(document.body, { childList: true, subtree: true, characterData: true });
      document.addEventListener('fullscreenchange', () => {
        placePanelForFullscreen();
        scheduleAutoRecognize();
      });
      document.addEventListener('keydown', event => {
        if (event.altKey && event.shiftKey && event.code === 'KeyB') {
          event.preventDefault();
          identify();
        }
      });
      scheduleAutoRecognize();
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
