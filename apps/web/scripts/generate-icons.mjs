import sharp from 'sharp'
import { writeFileSync, mkdirSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const outDir = join(__dirname, '..', 'public', 'icons')

mkdirSync(outDir, { recursive: true })

const sizes = [192, 512]

function svg(size, maskable = false) {
  const pad = Math.round(size * 0.18)
  const inner = size - pad * 2
  const cx = size / 2
  const cy = size / 2
  const bg = maskable ? '#6366F1' : 'none'
  const radius = size * 0.22

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#818CF8"/>
      <stop offset="50%" stop-color="#6366F1"/>
      <stop offset="100%" stop-color="#00FFA3"/>
    </linearGradient>
    <linearGradient id="g2" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#6366F1"/>
      <stop offset="100%" stop-color="#4338CA"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="${size * 0.04}" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect x="0" y="0" width="${size}" height="${size}" rx="${radius}" ry="${radius}" fill="${bg}"/>
  <g transform="translate(${pad}, ${pad})">
    <rect x="0" y="0" width="${inner}" height="${inner}" rx="${radius * 0.5}" fill="#13151A" stroke="#6366F1" stroke-width="${size * 0.015}"/>
    <circle cx="${inner * 0.5}" cy="${inner * 0.35}" r="${inner * 0.28}" fill="url(#g)" opacity="0.15"/>
    <path d="M${inner * 0.3} ${inner * 0.78} L${inner * 0.5} ${inner * 0.18} L${inner * 0.7} ${inner * 0.78}" fill="none" stroke="url(#g)" stroke-width="${inner * 0.1}" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)"/>
    <path d="M${inner * 0.38} ${inner * 0.6} L${inner * 0.62} ${inner * 0.6}" fill="none" stroke="url(#g2)" stroke-width="${inner * 0.06}" stroke-linecap="round"/>
  </g>
</svg>`
}

for (const size of sizes) {
  const s = svg(size, false)
  const buf = Buffer.from(s)
  await sharp(buf).resize(size, size).png().toFile(join(outDir, `icon-${size}x${size}.png`))
  console.log(`Created icon-${size}x${size}.png`)

  // Maskable variant for the 512 size
  if (size === 512) {
    const sm = svg(size, true)
    const buf2 = Buffer.from(sm)
    await sharp(buf2).resize(size, size).png().toFile(join(outDir, `icon-${size}x${size}-maskable.png`))
    console.log(`Created icon-${size}x${size}-maskable.png`)
  }
}
