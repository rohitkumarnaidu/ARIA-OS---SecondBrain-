const config = {
  ci: {
    collect: {
      numberOfRuns: 3,
      startServerCommand: 'cd apps/web && npm run start',
      url: ['http://localhost:3000', 'http://localhost:3000/dashboard', 'http://localhost:3000/tasks'],
    },
    upload: {
      target: 'temporary-public-storage',
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['error', { minScore: 0.95 }],
        'categories:best-practices': ['error', { minScore: 0.9 }],
        'categories:seo': ['error', { minScore: 1 }],
        'total-byte-weight': ['error', { maxNumericValue: 500000 }],
        'max-potential-fid': ['error', { maxNumericValue: 100 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'first-contentful-paint': ['error', { maxNumericValue: 1800 }],
        'interactive': ['error', { maxNumericValue: 3500 }],
        'uses-responsive-images': ['error', { minScore: 1 }],
        'offscreen-images': ['error', { minScore: 1 }],
        'uses-webp-images': ['error', { minScore: 0.9 }],
        'uses-optimized-images': ['error', { minScore: 0.9 }],
        'uses-text-compression': ['error', { minScore: 1 }],
        'uses-rel-preconnect': ['error', { minScore: 1 }],
        'redirects': ['error', { maxNumericValue: 0 }],
        'server-response-time': ['error', { maxNumericValue: 500 }],
      },
    },
  },
}

module.exports = config
