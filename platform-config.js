const PLATFORM_CONFIG = {
  beisen: {
    name: '北森',
    urlPatterns: ['beisen.com', 'bestalent.com', 'beisencloud.com', 'beisenc.com'],
    selectors: {
      question: [
        '.question-item', '.test-question', '.exam-question', '.question-container',
        '.subject-item', '[class*="question-item"]', '[class*="questionItem"]'
      ],
      stem: [
        '.question-stem', '.question-text', '.subject-text', '.question-content',
        '.stem', '[class*="question-title"]', '[class*="questionTitle"]'
      ],
      options: [
        '.option-item', '.answer-option', '.choice-item', '.answer-item',
        '[class*="option-item"]', '[class*="optionItem"]', 'label'
      ]
    }
  },
  iflytek: {
    name: '科大讯飞人才评估',
    urlPatterns: ['iflytek.ceping.com'],
    selectors: {
      question: [
        '.question-container__comp', '.question-container',
        '[class*="question-container"]'
      ],
      stem: [
        '.question-container__comp pre', '.question-container pre',
        'pre', '[class*="question-title"]'
      ],
      options: [
        '.single-choice__item', '.multiple-choice__item',
        '[class*="choice__item"]',
        'div[data-cls="tuozhuai-content"] span[class*="I6Yvw"]'
      ]
    }
  }
};

window.PLATFORM_CONFIG = PLATFORM_CONFIG;
