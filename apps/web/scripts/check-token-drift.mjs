import { readFileSync, existsSync, statSync, readdirSync } from 'node:fs'
import { resolve, dirname, relative, extname, sep } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const ROOT = resolve(__dirname, '..')

const IGNORE_DIRS = new Set([
  'node_modules', '.next', '.git', 'out', 'dist', 'build', 'coverage',
  'playwright-report', 'test-results', '__snapshots__', 'storybook-static',
])

const IGNORE_FILES = new Set([
  'tailwind.config.js', 'globals.css', '.eslintrc.json', 'next.config.js',
  'postcss.config.js', 'vitest.config.ts', 'playwright.config.ts',
])

// Patterns for hardcoded colors — match hex, rgb, rgba, hsl, hsla
const HARDCODED_RE = /(?:^|[^-\w#])((?:#[0-9a-fA-F]{3,8}|rgba?\(|hsla?\())/g

// Hardcoded shadow patterns (arbitrary box-shadow values)
const SHADOW_RE = /shadow-\[[^\]]+\]/g

// Arbitrary Tailwind color values
const ARBITRARY_BG_RE = /bg-\[#[^\]]+\]/g
const ARBITRARY_TEXT_RE = /text-\[#[^\]]+\]/g
const ARBITRARY_BORDER_RE = /border-\[#[^\]]+\]/g

// Test files get softer rules — only flag obvious violations
const TEST_FILE_RE = /\.(test|spec|stories?)\.(tsx?|jsx?)$/

function shouldIgnore(filePath) {
  const parts = filePath.split(sep)
  for (const p of parts) {
    if (IGNORE_DIRS.has(p)) return true
  }
  const basename = parts[parts.length - 1]
  return IGNORE_FILES.has(basename)
}

function scanFile(filePath) {
  const ext = extname(filePath)
  if (!['.ts', '.tsx', '.js', '.jsx', '.mjs', '.css'].includes(ext)) return []

  const issues = []
  const isTest = TEST_FILE_RE.test(filePath)
  const content = readFileSync(filePath, 'utf-8')
  const lines = content.split('\n')

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    const lineNum = i + 1

    // Skip lines that are comments
    const trimmed = line.trim()
    if (trimmed.startsWith('//') || trimmed.startsWith('/*') || trimmed.startsWith('*')) continue

    // Check hardcoded colors in className strings
    if (line.includes('className=') || line.includes('class=')) {
      // Check for arbitrary tailwind values
      let m
      while ((m = ARBITRARY_BG_RE.exec(line)) !== null) {
        issues.push({ file: filePath, line: lineNum, issue: `Hardcoded bg-color: ${m[0]}. Use bg-background-* or bg-accent-* instead.`, severity: 'error' })
      }
      while ((m = ARBITRARY_TEXT_RE.exec(line)) !== null) {
        issues.push({ file: filePath, line: lineNum, issue: `Hardcoded text-color: ${m[0]}. Use text-text-* instead.`, severity: 'error' })
      }
      while ((m = ARBITRARY_BORDER_RE.exec(line)) !== null) {
        issues.push({ file: filePath, line: lineNum, issue: `Hardcoded border-color: ${m[0]}. Use border-border-* instead.`, severity: 'error' })
      }
      while ((m = SHADOW_RE.exec(line)) !== null) {
        issues.push({ file: filePath, line: lineNum, issue: `Arbitrary shadow: ${m[0]}. Use shadow-glow-*, shadow-neon-*, or shadow-cyber-* instead.`, severity: 'error' })
      }
    }

    // Check CSS files for hardcoded colors not using CSS variables
    if (ext === '.css' && !line.includes('var(--') && !line.includes('inherit') && !line.includes('transparent') && !line.includes('currentColor')) {
      let m
      while ((m = HARDCODED_RE.exec(line)) !== null) {
        if (isTest) continue
        issues.push({ file: filePath, line: lineNum, issue: `Hardcoded color value: ${m[1]}. Use CSS var(--*) instead.`, severity: 'error' })
      }
    }
  }

  return issues
}

function main() {
  const args = process.argv.slice(2)
  const isAutoFix = args.includes('--fix')
  const scanDirs = [resolve(ROOT, 'app'), resolve(ROOT, 'components'), resolve(ROOT, 'hooks'), resolve(ROOT, 'lib'), resolve(ROOT, 'styles')]

  console.log('[check:drift] Scanning for hardcoded color values...\n')

  let allIssues = []
  let scannedCount = 0

  for (const dir of scanDirs) {
    if (!existsSync(dir)) continue
    const entries = collectFiles(dir)
    for (const file of entries) {
      if (shouldIgnore(file)) continue
      scannedCount++
      try {
        const issues = scanFile(file)
        allIssues = allIssues.concat(issues)
      } catch {
        // skip unreadable files
      }
    }
  }

  const errors = allIssues.filter(i => i.severity === 'error')
  const warnings = allIssues.filter(i => i.severity === 'warn')

  console.log(`Scanned ${scannedCount} files`)
  console.log(`Found ${errors.length} errors, ${warnings.length} warnings\n`)

  if (errors.length > 0) {
    for (const err of errors) {
      const relPath = relative(ROOT, err.file)
      console.log(`  ✗ ${relPath}:${err.line} — ${err.issue}`)
    }
    if (isAutoFix) {
      console.log('\n  Auto-fix mode enabled. Run `npm run figma:sync` to review token mappings.')
    }
    console.log(`\n[check:drift] ✗ FAILED — ${errors.length} hardcoded color${errors.length > 1 ? 's' : ''} found.`)
    console.log('  Tip: Use `npm run figma:sync` to update tokens, then replace violations manually.')
    process.exit(1)
  }

  console.log('[check:drift] ✓ PASSED — No hardcoded colors found.')
}

function collectFiles(dir) {
  const result = []
  // readdirSync imported at top of file
  try {
    const entries = readdirSync(dir, { withFileTypes: true })
    for (const entry of entries) {
      const full = resolve(dir, entry.name)
      if (entry.isDirectory()) {
        if (!IGNORE_DIRS.has(entry.name)) {
          result.push(...collectFiles(full))
        }
      } else {
        result.push(full)
      }
    }
  } catch { /* skip */ }
  return result
}

main()
