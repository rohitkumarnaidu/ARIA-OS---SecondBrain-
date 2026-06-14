'use client'

import { Component, ErrorInfo, ReactNode } from 'react'
import * as Sentry from '@sentry/nextjs'
import { AlertTriangle, RefreshCw, Home } from 'lucide-react'
import Link from 'next/link'

interface Props {
  children: ReactNode
  name?: string
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = { hasError: false, error: null }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    Sentry.captureException(error, {
      extra: { componentStack: errorInfo.componentStack },
      tags: { boundary: this.props.name || 'unknown' },
    })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback

      return (
        <div role="alert" className="flex flex-col items-center justify-center p-8 text-center">
          <AlertTriangle size={48} className="text-accent-warning mb-4" aria-hidden="true" />
          <h2 className="text-xl font-display font-semibold text-text-primary mb-2">
            {this.props.name || 'Section'} failed to load
          </h2>
          <p className="text-text-secondary mb-4 text-sm max-w-md">
            {this.state.error?.message || 'An unexpected error occurred'}
          </p>
          <div className="flex items-center gap-3">
            <button
              onClick={() => this.setState({ hasError: false, error: null })}
              className="inline-flex items-center gap-2 bg-accent-primary text-white px-4 py-2 rounded-lg font-medium text-sm hover:bg-accent-primaryHover transition-colors"
            >
              <RefreshCw size={16} /> Try again
            </button>
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 bg-background-elevated text-text-primary px-4 py-2 rounded-lg font-medium text-sm border border-border hover:bg-border transition-colors"
            >
              <Home size={16} /> Dashboard
            </Link>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
