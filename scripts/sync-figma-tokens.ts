/**
 * Figma Token Sync Script
 * 
 * Reads figma-tokens.json (exported from Figma Design Token Manager plugin)
 * and validates the structure matches expected ARIA OS token categories.
 * 
 * Usage: npm run figma:sync
 * Input: ./figma-tokens.json
 * 
 * Expected categories:
 *   colors (light + dark)
 *   typography (fonts, sizes, weights, lineHeights)
 *   spacing (scale)
 *   shadows (glow, neon, cyber, focus)
 *   borderRadius (scale)
 *   opacity (scale)
 *   motion (durations, easings)
 *   zIndex (layers)
 */

import { readFileSync, existsSync } from 'fs'
import { join } from 'path'

const REQUIRED_CATEGORIES = ['colors', 'typography', 'spacing', 'shadows', 'borderRadius', 'opacity', 'motion', 'zIndex']

interface ValidationResult {
  valid: boolean
  errors: string[]
  categories: string[]
  tokenCount: number
}

function validateTokens(jsonPath: string): ValidationResult {
  const errors: string[] = []

  if (!existsSync(jsonPath)) {
    return { valid: false, errors: [`Token file not found: ${jsonPath}`], categories: [], tokenCount: 0 }
  }

  let tokens: Record<string, unknown>
  try {
    const content = readFileSync(jsonPath, 'utf-8')
    tokens = JSON.parse(content)
  } catch {
    return { valid: false, errors: ['Invalid JSON in token file'], categories: [], tokenCount: 0 }
  }

  const categories = Object.keys(tokens)
  const missingCategories = REQUIRED_CATEGORIES.filter(c => !categories.includes(c))

  if (missingCategories.length > 0) {
    errors.push(`Missing required categories: ${missingCategories.join(', ')}`)
  }

  if (!tokens.colors) {
    errors.push('colors category is required')
  } else if (typeof tokens.colors === 'object') {
    const colorModes = Object.keys(tokens.colors as object)
    if (!colorModes.includes('light') && !colorModes.includes('dark')) {
      errors.push('colors must include light and/or dark mode variants')
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    categories,
    tokenCount: categories.reduce((count, cat) => count + Object.keys((tokens[cat] as object) || {}).length, 0),
  }
}

function main() {
  const args = process.argv.slice(2)
  const jsonPath = args[0] || join(process.cwd(), 'figma-tokens.json')

  console.log(`\n  🔄 Figma Token Sync\n`)
  console.log(`  Input: ${jsonPath}\n`)

  const result = validateTokens(jsonPath)

  if (result.valid) {
    console.log(`  ✅ Validation passed`)
    console.log(`  Categories: ${result.categories.join(', ')}`)
    console.log(`  Token count: ${result.tokenCount}\n`)
    process.exit(0)
  } else {
    console.log(`  ❌ Validation failed:\n`)
    result.errors.forEach(e => console.log(`     • ${e}`))
    console.log()
    process.exit(1)
  }
}

main()
