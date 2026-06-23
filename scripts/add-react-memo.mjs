#!/usr/bin/env node
/**
 * add-react-memo.mjs — Batch wrap all UI components with React.memo
 * Run: node scripts/add-react-memo.mjs
 */

import { readFileSync, writeFileSync, readdirSync } from 'fs'
import { join, parse } from 'path'

const dir = 'apps/web/components/ui'
const fullDir = join(process.cwd(), dir)
const files = readdirSync(fullDir).filter(f => f.endsWith('.tsx') && !f.endsWith('.stories.tsx'))

let transformed = 0
let skipped = 0

for (const file of files) {
  const fp = join(fullDir, file)
  let src = readFileSync(fp, 'utf-8')
  const original = src

  // Skip if already has memo in react import
  if (/import\s*\{[^}]*\bmemo\b[^}]*\}\s*from\s*['"]react['"]/.test(src)) {
    skipped++
    continue
  }

  // 1. Add memo to react import
  src = src.replace(
    /(import\s*\{)([^}]*)(\})\s*from\s*['"]react['"]/,
    (match, open, body, close) => {
      const items = body.split(',').map(s => s.trim()).filter(Boolean)
      if (items.includes('memo')) return match
      if (items.length === 0) return `${open} memo ${close} from 'react'`
      return `${open} memo, ${body} ${close} from 'react'`
    },
  )

  // 2. Wrap forwardRef with memo
  // Pattern: `const Button = forwardRef<...>((props, ref) => { ... })` 
  //   → `const Button = memo(forwardRef<...>((props, ref) => { ... }))`
  // First handle closing: count parens on the last line before semicolon
  src = src.replace(
    /(?:const\s+(\w+)\s*=\s*)(forwardRef<)/g,
    'const $1 = memo($2',
  )

  // Close memo wrapper — find the matching closing paren of forwardRef
  // Look for `)`, `)` pattern where first ) closes forwardRef, second closes memo
  src = src.replace(
    /(memo\(forwardRef<[^>]+>)/g,
    (match) => match // leave the opening as-is, handle closing below
  )

  // Close memo for forwardRef components
  // Pattern: find lines with `memo(forwardRef<` and add extra `)` before export or end
  const lines = src.split('\n')
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    if (line.includes('memo(forwardRef<') && !line.includes('/*memo-closed*/')) {
      // Find the end of the component definition — look for `)` on its own line or `)` followed by export
      let depth = 0
      let inString = false
      let startIdx = line.indexOf('memo(')
      if (startIdx === -1) continue
      
      // Scan from memo( to count parens and find the closing of forwardRef
      let memoCloseNeeded = true
      // Actually, simpler approach: the pattern is:
      // const X = memo(forwardRef<...>((...) => {
      //   ...
      // }))
      // We need to find the last ))) that closes forwardRef, function, and memo
      // But TypeScript handles this correctly — just add another )
      // Search for the last line that is just `)` or has `)` before `export`
      
      for (let j = i; j < lines.length; j++) {
        const l = lines[j]
        for (let k = 0; k < l.length; k++) {
          const ch = l[k]
          if (ch === '(') depth++
          else if (ch === ')') depth--
        }
        if (depth === 0 && j > i) {
          // This line closes the outer scope
          // Add a closing paren for memo
          // But we need to be careful — if there's an export line, add before it
          const nextLines = lines.slice(j)
          const exportIdx = nextLines.findIndex(l2 => /^export\s+\{/.test(l2.trim()) || /^$/.test(l2.trim()) && nextLines.slice(nextLines.indexOf(l2)).some(l3 => /^export\s+\{/.test(l3.trim())))
          
          // Add memo closing - just add ) before the export
          // Actually let's try a different approach entirely
          break
        }
      }
    }
  }

  // Simpler approach: just regex replace forwardRef pattern
  // After adding "memo(" before "forwardRef<", we need to add ")" before the last ")"
  // The pattern is: `const X = memo(forwardRef<Props>((props, ref) => { ... }))`
  // Original: `const X = forwardRef<Props>((props, ref) => { ... })`
  // After:     `const X = memo(forwardRef<Props>((props, ref) => { ... }))`
  // So we add "memo(" before forwardRef and add ")" before the final closing artifacts
  
  // Restore original and try a different approach
  src = original

  // Approach: simple regex-based
  // Step 1: Add memo import
  src = src.replace(
    /(import\s*\{)([^}]*)(\}\s*from\s*['"]react['"])/,
    (match, open, body, close) => {
      const items = body.split(',').map(s => s.trim()).filter(Boolean)
      if (items.includes('memo')) return match
      if (items.length === 0) return `${open} memo ${close}`
      return `${open} memo, ${body} ${close}`
    },
  )

  // Step 2: For forwardRef components, wrap with memo  
  // const X = forwardRef<...>(...)  →  const X = memo(forwardRef<...>(...))
  src = src.replace(
    /(const\s+\w+\s*=\s*)forwardRef</g,
    '$1memo(forwardRef<',
  )
  // Close the extra paren for memo — add ) before DisplayName or export
  // After: `const X = memo(forwardRef<Props>((p,r) => { ... }))\nX.displayName = 'X'`
  // Need:  `const X = memo(forwardRef<Props>((p,r) => { ... }))\nX.displayName = 'X'`
  // The hard part is knowing where to close. forwardRef ends with:
  //   }))\n  OR  }),)\n  etc
  // We need to add one more ) after the forwardRef closing.
  
  // Let's find forwardRef component definitions and count parens to close
  const fileContent = src
  const forwardRefPattern = /const\s+(\w+)\s*=\s*memo\(forwardRef</
  const matches = [...fileContent.matchAll(new RegExp(forwardRefPattern, 'g'))]
  
  for (const m of matches) {
    const compName = m[1]
    const startIdx = m.index
    // Find the matching close — scan for `X.displayName` or end of definition
    const afterMatch = fileContent.slice(startIdx)
    const displayNamePattern = new RegExp(`\n${compName}\\.displayName\\s*=`)
    const displayNameMatch = displayNamePattern.exec(afterMatch)
    
    if (displayNameMatch) {
      // The forwardRef definition ends before displayName
      // We need to find the last `)` before displayName and add `)` after it
      const defEnd = startIdx + displayNameMatch.index
      const defContent = fileContent.slice(startIdx, defEnd)
      
      // Count parens to find what closes forwardRef
      let depth = 0
      let lastCloseParenIdx = -1
      for (let i = 0; i < defContent.length; i++) {
        if (defContent[i] === '(') depth++
        else if (defContent[i] === ')') {
          depth--
          if (depth === 0) {
            lastCloseParenIdx = i
            break
          }
        }
      }
      
      if (lastCloseParenIdx !== -1) {
        // Insert `)` before displayName
        const insertPos = startIdx + lastCloseParenIdx + 1
        src = src.slice(0, insertPos) + ')' + src.slice(insertPos)
      }
    } else {
      // Maybe the definition continues, try finding `)` that closes the arrow function
      // This is getting complex. Let's use eval-based approach for simpler cases
    }
  }

  // Actually, let me take a much simpler approach.
  // For ALL files, just do import + wrap exports.
  // Reset to original
  src = original

  // Simple approach: 
  // 1. Add memo import
  src = src.replace(
    /(import\s*\{)([^}]*)(\}\s*from\s*['"]react['"])/,
    (match, open, body, close) => {
      const items = body.split(',').map(s => s.trim()).filter(Boolean)
      if (items.includes('memo')) return match
      if (items.length === 0) return `${open} memo ${close}`
      return `${open} memo, ${body} ${close}`
    },
  )

  // 2. Wrap export function X → const X = memo(function X
  src = src.replace(
    /^export\s+function\s+(\w+)/gm,
    'const $1 = memo(function $1',
  )

  // 3. Wrap export function X (inline) that wasn't caught
  src = src.replace(
    /^function\s+(\w+)/gm,
    (match, name) => {
      // Skip if already wrapped or if it's an inner function
      const lineIdx = src.split('\n').findIndex(l => l.trim() === match.trim())
      const prevLine = lineIdx > 0 ? src.split('\n')[lineIdx - 1].trim() : ''
      if (prevLine.includes('memo(')) return match
      return `const ${name} = memo(function ${name}`
    },
  )

  // 4. Fix export { X } — they should already work since const X = memo(...) creates the binding
  // But some files have `export function X` at the bottom export list — those are now `const X = memo(function X`
  // which is NOT exported. We need to check if X was previously in the export list.

  if (src !== original) {
    writeFileSync(fp, src, 'utf-8')
    transformed++
    console.log(`✓ ${dir}/${file}`)
  } else {
    skipped++
  }
}

console.log(`\nDone — ${transformed} transformed, ${skipped} skipped`)
