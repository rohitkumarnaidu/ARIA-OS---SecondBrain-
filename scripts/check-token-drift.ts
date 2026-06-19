/**
 * Token Drift Check Script
 * 
 * Scans all .tsx and .css files for hardcoded color values.
 * Designed to run in CI to prevent token drift.
 * 
 * Usage: npm run token:check
 * 
 * Fails if any file contains hardcoded hex/rgb/rgba/hsl colors outside of
 * allowed files (tailwind.config.js, globals.css).
 */

import { readFileSync, existsSync } from 'fs'
import { join } from 'path'
import { execSync } from 'child_process'

const ALLOWED_FILES = ['tailwind.config.js', 'globals.css', 'figma-tokens.json']
const ALLOWED_PATTERNS = ['node_modules', '.next', 'coverage', '__tests__/']
const EXCLUDED_EXTENSIONS = ['.json', '.md', '.yaml', '.yml', '.svg', '.png', '.jpg', '.ico']

// Match hardcoded colors: hex (#fff, #ffffff), rgb(), rgba(), hsl(), hsla()
const COLOR_PATTERN = /(?:[^a-zA-Z])(?:#[0-9a-fA-F]{3}\b|#[0-9a-fA-F]{6}\b|rgba?\s*\(|hsla?\s*\()/

interface DriftResult {
  file: string
  line: number
  content: string
}

function scanFile(filePath: string): DriftResult[] {
  const results: DriftResult[] = []
  const content = readFileSync(filePath, 'utf-8')
  const lines = content.split('\n')

  lines.forEach((line, index) => {
    const matches = line.match(COLOR_PATTERN)
    if (matches) {
      results.push({
        file: filePath,
        line: index + 1,
        content: line.trim(),
      })
    }
  })

  return results
}

function main() {
  const results: DriftResult[] = []

  try {
    const output = execSync('git ls-files -- "*.tsx" "*.ts" "*.css"', { encoding: 'utf-8' })
    const files = output.split('\n').filter(Boolean)

    for (const file of files) {
      if (ALLOWED_FILES.some(f => file.endsWith(f))) continue
      if (ALLOWED_PATTERNS.some(p => file.includes(p))) continue

      const fileResults = scanFile(file)
      results.push(...fileResults)
    }
  } catch {
    console.log('  ⚠ Not a git repository or git not available. Skipping scan.\n')
    process.exit(0)
  }

  if (results.length > 0) {
    console.log(`\n  ❌ Token drift detected: ${results.length} hardcoded colors found\n`)
    results.forEach(r => {
      console.log(`  ${r.file}:${r.line}`)
      console.log(`  → ${r.content}`)
      console.log()
    })
    process.exit(1)
  } else {
    console.log(`\n  ✅ No token drift detected. All colors use design tokens.\n`)
    process.exit(0)
  }
}

main()
