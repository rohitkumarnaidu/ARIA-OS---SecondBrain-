module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [2, 'always', ['feat', 'fix', 'chore', 'docs', 'style', 'refactor', 'perf', 'test', 'ci', 'build', 'revert', 'security']],
    'scope-enum': [2, 'always', ['api', 'web', 'scheduler', 'ai', 'prompts', 'infra', 'deps', 'release']],
    'subject-case': [2, 'always', 'sentence-case'],
    'header-max-length': [2, 'always', 72],
    'body-max-line-length': [2, 'always', 100]
  }
}
