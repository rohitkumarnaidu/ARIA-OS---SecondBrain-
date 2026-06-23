/**
 * Package Health Check Script
 *
 * Reads package.json and requirements.txt, checks for:
 * - Deprecated packages (reactflow → @xyflow/react, next-pwa → @serwist/next)
 * - Outdated major versions via npm outdated
 *
 * Usage: npx ts-node --esm scripts/check-packages.ts
 * Exits with code 1 if issues found, 0 if clean.
 */

import { readFileSync } from 'fs'
import { join } from 'path'
import { execSync } from 'child_process'

const ROOT = join(__dirname, '..')
const WEB_PKG = join(ROOT, 'apps/web/package.json')
const API_REQ = join(ROOT, 'apps/api/requirements.txt')

interface PackageIssue {
  type: 'deprecated' | 'outdated'
  package: string
  message: string
}

const DEPRECATED_MAP: Record<string, string> = {
  reactflow: '@xyflow/react',
  'react-flow-renderer': '@xyflow/react',
  'next-pwa': '@serwist/next',
}

function checkPackageJson(): PackageIssue[] {
  const issues: PackageIssue[] = []
  const pkg = JSON.parse(readFileSync(WEB_PKG, 'utf-8'))
  const allDeps = { ...pkg.dependencies, ...pkg.devDependencies } as Record<string, string>

  for (const [name, version] of Object.entries(allDeps)) {
    if (DEPRECATED_MAP[name]) {
      issues.push({
        type: 'deprecated',
        package: name,
        message: `${name} is deprecated. Replace with ${DEPRECATED_MAP[name]}`,
      })
    }
  }

  return issues
}

function checkOutdatedPackages(): PackageIssue[] {
  const issues: PackageIssue[] = []

  try {
    const output = execSync('npm outdated --json 2>&1 || true', {
      cwd: join(ROOT, 'apps/web'),
      encoding: 'utf-8',
      stdio: ['pipe', 'pipe', 'pipe'],
    })

    if (!output.trim()) return issues

    const outdated = JSON.parse(output)
    for (const [name, info] of Object.entries(outdated) as [string, { current: string; wanted: string; latest: string }][]) {
      const currentMajor = parseInt(info.current.split('.')[0], 10)
      const latestMajor = parseInt(info.latest.split('.')[0], 10)

      if (latestMajor > currentMajor) {
        issues.push({
          type: 'outdated',
          package: name,
          message: `${name} ${info.current} → latest ${info.latest} (major version bump)`,
        })
      }
    }
  } catch {
    issues.push({
      type: 'outdated',
      package: 'npm-outdated',
      message: 'Could not run npm outdated (npm not available or not installed)',
    })
  }

  return issues
}

function checkRequirementsTxt(): PackageIssue[] {
  const issues: PackageIssue[] = []
  const content = readFileSync(API_REQ, 'utf-8')

  const deprecatedPip: Record<string, string> = {
    'pytz': 'use zoneinfo (Python 3.9+) or python-dateutil',
  }

  for (const line of content.split('\n')) {
    const trimmed = line.trim()
    if (!trimmed || trimmed.startsWith('#')) continue

    const match = trimmed.match(/^([a-zA-Z0-9_.-]+)/)
    if (match) {
      const name = match[1].toLowerCase()
      if (deprecatedPip[name]) {
        issues.push({
          type: 'deprecated',
          package: name,
          message: `${name} is deprecated. ${deprecatedPip[name]}`,
        })
      }
    }
  }

  return issues
}

function main() {
  const allIssues: PackageIssue[] = [
    ...checkPackageJson(),
    ...checkOutdatedPackages(),
    ...checkRequirementsTxt(),
  ]

  if (allIssues.length === 0) {
    console.log('\n  ✅ All packages healthy — no deprecated or outdated major versions found.\n')
    process.exit(0)
  }

  console.log(`\n  ❌ Found ${allIssues.length} package issue(s):\n`)

  for (const issue of allIssues) {
    const icon = issue.type === 'deprecated' ? '⚠' : '↓'
    console.log(`  ${icon}  [${issue.type}] ${issue.package}`)
    console.log(`     ${issue.message}`)
    console.log()
  }

  process.exit(1)
}

main()
