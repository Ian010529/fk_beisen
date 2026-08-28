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
  }
};

window.PLATFORM_CONFIG = PLATFORM_CONFIG;
