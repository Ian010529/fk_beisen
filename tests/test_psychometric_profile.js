const assert = require('node:assert/strict');
const profile = require('../psychometric-profile.js');

const questionCount = Object.values(profile.answerCategories)
  .reduce((total, questions) => total + questions.length, 0);

assert.equal(questionCount, 19);
assert.equal(profile.adjectiveRanking.length, 15);
assert.equal(profile.defaultAnswer, '非常不符合');
assert.ok(profile.answerCategories['比较符合'].includes('我喜欢与他人合作完成任务'));

console.log('psychometric profile: ok');
