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
  },
  talebase: {
    name: 'TaleBase TAS 智选',
    urlPatterns: ['tas.talebase.com'],
    selectors: {
      question: [
        '.tbc-question', '.question-box', '.tbc-single-choice',
        '.tbc-single-choice360', '.tbc-force-choice', '[class*="tbc-scale"]'
      ],
      stem: [
        '.tbc-single-choice__stem', '.tbc-single-choice360__stem',
        '.tbc-force-choice__stem', '.tbc-force__stem',
        '.tbc-scale__stem', '.tbc-scale360__item__stem', '.ques_stem'
      ],
      options: [
        '.tbc-single-choice__option',
        '.tbc-single-choice360__table__item__option__item',
        '.tbc-force-choice__option-item',
        '.tbc-scale360__item__option__item',
        'label'
      ]
    }
  }
};

window.PLATFORM_CONFIG = PLATFORM_CONFIG;
