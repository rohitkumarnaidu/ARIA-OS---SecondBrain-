/**
 * Accessibility Lint Script
 *
 * Scans .tsx files for common a11y issues:
 * - Missing alt attributes on <img> tags
 * - Missing aria-label on interactive elements without visible text
 *
 * Usage: npx ts-node --esm scripts/lint-a11y.ts
 * Exits with code 1 if issues found, 0 if clean.
 */

import { readFileSync, existsSync } from 'fs'
import { join } from 'path'
import { execSync } from 'child_process'

const ROOT = join(__dirname, '..')
const EXCLUDED_DIRS = ['node_modules', '.next', 'coverage', '__tests__']

interface A11yIssue {
  file: string
  line: number
  type: 'missing-alt' | 'missing-aria-label'
  element: string
}

function getTsxFiles(): string[] {
  try {
    const output = execSync('git ls-files -- "*.tsx"', { cwd: ROOT, encoding: 'utf-8' })
    return output.split('\n').filter(Boolean).filter(f => !EXCLUDED_DIRS.some(d => f.includes(d)))
  } catch {
    // Fallback: walk directory
    const { globSync } = require('glob') as { globSync: (p: string) => string[] }
    return globSync('**/*.tsx', { cwd: ROOT, ignore: ['**/node_modules/**', '**/.next/**'] })
  }
}

function scanFile(filePath: string): A11yIssue[] {
  const issues: A11yIssue[] = []
  const absolutePath = join(ROOT, filePath)

  if (!existsSync(absolutePath)) return issues

  const content = readFileSync(absolutePath, 'utf-8')
  const lines = content.split('\n')

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    const lineNum = i + 1

    // Check <img> tags for alt attribute
    const imgRegex = /<img\s[^>]*>/gi
    let imgMatch: RegExpExecArray | null
    while ((imgMatch = imgRegex.exec(line)) !== null) {
      if (!/alt\s*=/i.test(imgMatch[0])) {
        issues.push({
          file: filePath,
          line: lineNum,
          type: 'missing-alt',
          element: imgMatch[0].substring(0, 80),
        })
      }
    }

    // Check for Image component from next/image without alt
    const nextImgRegex = /<Image\s[^>]*\/?\s*>/gi
    let nextImgMatch: RegExpExecArray | null
    while ((nextImgMatch = nextImgRegex.exec(line)) !== null) {
      if (!/alt\s*=/i.test(nextImgMatch[0])) {
        issues.push({
          file: filePath,
          line: lineNum,
          type: 'missing-alt',
          element: nextImgMatch[0].substring(0, 80),
        })
      }
    }

    // Check interactive elements without visible text or aria-label
    const interactiveTags = ['button', 'a', 'input', 'select', 'textarea']
    for (const tag of interactiveTags) {
      const openRegex = new RegExp(`<${tag}[^>]*>`, 'gi')
      let match: RegExpExecArray | null
      while ((match = openRegex.exec(line)) !== null) {
        const element = match[0]

        // Skip if it has aria-label or aria-labelledby
        if (/aria-label\s*=|aria-labelledby\s*=/i.test(element)) continue

        // Skip <a> with href (has navigation purpose)
        if (tag === 'a' && /href\s*=/i.test(element)) continue

        // Skip inputs with type="hidden"
        if (tag === 'input' && /type\s*=\s*["']hidden["']/i.test(element)) continue

        // Check if it has visible text content (on the same line)
        const hasVisibleText = />[^<\s]/.test(element)

        // For buttons: check if there's visible text
        if (tag === 'button' && !hasVisibleText) {
          // Check next line for content
          const nextLine = lines[i + 1] || ''
          const hasContent = /[^\s]/.test(nextLine) && !nextLine.includes('<')

          if (!hasContent) {
            issues.push({
              file: filePath,
              line: lineNum,
              type: 'missing-aria-label',
              element: element.substring(0, 80),
            })
          }
        }
      }
    }
  }

  return issues
}

function main() {
  const files = getTsxFiles()
  console.log(`\n  ♿ Scanning ${files.length} .tsx files for accessibility issues...\n`)

  let totalIssues = 0
  const groupedByType: Record<string, A11yIssue[]> = { 'missing-alt': [], 'missing-aria-label': [] }

  for (const file of files) {
    const issues = scanFile(file)
    for (const issue of issues) {
      groupedByType[issue.type]?.push(issue)
      totalIssues++
    }
  }

  if (totalIssues === 0) {
    console.log('  ✅ No accessibility issues found.\n')
    process.exit(0)
  }

  console.log(`  ❌ Found ${totalIssues} accessibility issue(s):\n`)

  if (groupedByType['missing-alt'].length > 0) {
    console.log(`  Missing alt attributes (${groupedByType['missing-alt'].length}):`)
    for (const issue of groupedByType['missing-alt']) {
      console.log(`    ${issue.file}:${issue.line}`)
      console.log(`    → ${issue.element}`)
      console.log()
    }
  }

  if (groupedByType['missing-aria-label'].length > 0) {
    console.log(`  Missing aria-label on interactive elements (${groupedByType['missing-aria-label'].length}):`)
    for (const issue of groupedByType['missing-aria-label']) {
      console.log(`    ${issue.file}:${issue.line}`)
      console.log(`    → ${issue.element}`)
      console.log()
    }
  }

  process.exit(1)
}

main()
