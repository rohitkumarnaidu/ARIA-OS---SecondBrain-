import { readFileSync, writeFileSync, existsSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const ROOT = resolve(__dirname, '..')
const TOKENS_PATH = resolve(ROOT, '../../docs/design/tokens/tokens-studio.json')
const TAILWIND_PATH = resolve(ROOT, 'tailwind.config.js')
const GLOBALS_PATH = resolve(ROOT, 'styles/globals.css')

const REQUIREMENTS = [
  'color.primitive',
  'color.semantic',
  'color.chart',
  'typography',
  'spacing',
  'borderRadius',
  'boxShadow',
  'motion',
  'opacity',
  'zIndex',
]

function validateTokens(tokens) {
  const missing = REQUIREMENTS.filter(r => {
    const parts = r.split('.')
    let curr = tokens
    for (const p of parts) {
      curr = curr?.[p]
    }
    return !curr
  })
  if (missing.length > 0) {
    console.error(`[figma:sync] WARN — Token categories missing: ${missing.join(', ')}`)
  }
}

function extractCSSVars(tokens, prefix = '') {
  const vars = []
  for (const [key, val] of Object.entries(tokens)) {
    if (!val || key.startsWith('$')) continue
    if (val.type === 'color') {
      vars.push({ name: `${prefix}${key}`, value: val.value })
    } else if (val.type === 'dimension' && typeof val.value === 'number') {
      vars.push({ name: `${prefix}${key}`, value: `${val.value}px` })
    } else if (val.type === 'number') {
      const suffix = prefix.endsWith('opacity-') || prefix.endsWith('z-index-') ? '' : ''
      vars.push({ name: `${prefix}${key}`, value: val.value })
    } else if (val.type === 'string') {
      vars.push({ name: `${prefix}${key}`, value: `"${val.value}"` })
    } else if (val.type === 'shadow') {
      let shadow = val.value
      if (typeof shadow === 'object') {
        const { x = 0, y = 0, blur = 0, spread = 0, color = '#000' } = shadow
        shadow = `${x}px ${y}px ${blur}px ${spread}px ${color}`
      }
      vars.push({ name: `${prefix}${key}`, value: shadow })
    } else if (val.type === 'typography') {
      const tv = val.value
      if (tv.fontFamily) vars.push({ name: `${prefix}${key}-font-family`, value: tv.fontFamily })
      if (tv.fontWeight) vars.push({ name: `${prefix}${key}-font-weight`, value: tv.fontWeight })
      if (tv.fontSize) vars.push({ name: `${prefix}${key}-font-size`, value: typeof tv.fontSize === 'number' ? `${tv.fontSize}px` : tv.fontSize })
      if (tv.lineHeight) vars.push({ name: `${prefix}${key}-line-height`, value: typeof tv.lineHeight === 'number' ? `${tv.lineHeight}px` : tv.lineHeight })
      if (tv.letterSpacing) vars.push({ name: `${prefix}${key}-letter-spacing`, value: typeof tv.letterSpacing === 'number' ? `${tv.letterSpacing}px` : tv.letterSpacing })
    } else if (val.type === 'transition' || val.type === 'motion') {
      const mv = val.value
      if (typeof mv === 'object') {
        if (mv.duration) vars.push({ name: `${prefix}${key}-duration`, value: mv.duration })
        if (mv.easing) vars.push({ name: `${prefix}${key}-easing`, value: mv.easing })
        if (mv.delay) vars.push({ name: `${prefix}${key}-delay`, value: mv.delay })
      }
    } else if (val.type === 'borderRadius') {
      let br = val.value
      if (typeof br === 'object') {
        br = Object.values(br).filter(v => typeof v === 'number').join('px ') + 'px'
      }
      vars.push({ name: `${prefix}${key}`, value: typeof br === 'number' ? `${br}px` : br })
    } else if (typeof val === 'object' && !Array.isArray(val)) {
      vars.push(...extractCSSVars(val, `${prefix}${key}-`))
    }
  }
  return vars
}

function generateCSS(vars) {
  const lines = vars.map(v => `  --${v.name.replace(/_/g, '-')}: ${v.value};`)
  return `:root {\n${lines.join('\n')}\n}\n`
}

function updateTailwindConfig(cssVars) {
  if (!existsSync(TAILWIND_PATH)) {
    console.warn('[figma:sync] tailwind.config.js not found — skipping.')
    return false
  }
  console.log(`[figma:sync] ✓ tailwind.config.js exists (${cssVars.length} token references)`)
  return true
}

function updateGlobalsCSS(cssVars) {
  if (!existsSync(GLOBALS_PATH)) {
    console.warn('[figma:sync] globals.css not found — skipping.')
    return false
  }
  const css = generateCSS(cssVars)
  writeFileSync(resolve(ROOT, 'scripts/.generated-tokens.css'), css, 'utf-8')
  console.log(`[figma:sync] ✓ Generated ${cssVars.length} CSS custom properties → scripts/.generated-tokens.css`)
  console.log(`[figma:sync]   → Review and merge vars into ${GLOBALS_PATH}`)
  return true
}

function main() {
  if (!existsSync(TOKENS_PATH)) {
    console.error(`[figma:sync] ✗ tokens-studio.json not found at:\n  ${TOKENS_PATH}`)
    console.log(`[figma:sync]   Export from Figma using Design Tokens plugin and save to that path.`)
    process.exit(1)
  }

  console.log(`[figma:sync] Reading tokens from ${TOKENS_PATH}`)
  const raw = readFileSync(TOKENS_PATH, 'utf-8')
  const tokens = JSON.parse(raw)
  validateTokens(tokens)

  const cssVars = extractCSSVars(tokens)
  console.log(`[figma:sync] Found ${cssVars.length} token values`)

  updateTailwindConfig(cssVars)
  updateGlobalsCSS(cssVars)

  console.log(`[figma:sync] ✓ Token sync complete. Run \`git diff\` to review changes.`)
}

main()
