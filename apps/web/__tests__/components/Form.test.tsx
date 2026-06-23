import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FormField, FormLabel, FormControl, FormMessage, FormDescription } from '@/components/ui/Form'

describe('Form', () => {
  describe('FormField', () => {
    it('renders with children', () => {
      render(<FormField><input /></FormField>)
      expect(document.querySelector('input')).toBeInTheDocument()
    })

    it('applies custom className', () => {
      render(<FormField className="custom"><input /></FormField>)
      expect(document.querySelector('input')?.closest('div')).toHaveClass('custom')
    })
  })

  describe('FormLabel', () => {
    it('renders label text', () => {
      render(<FormField name="email"><FormLabel>Email</FormLabel></FormField>)
      expect(screen.getByText('Email')).toBeInTheDocument()
    })
  })

  describe('FormControl', () => {
    it('renders children', () => {
      render(<FormField><FormControl><input data-testid="ctrl" /></FormControl></FormField>)
      expect(screen.getByTestId('ctrl')).toBeInTheDocument()
    })
  })

  describe('FormMessage', () => {
    it('renders error message', () => {
      render(<FormField error="Field is required"><FormMessage /></FormField>)
      expect(screen.getByText('Field is required')).toBeInTheDocument()
    })
  })

  describe('FormDescription', () => {
    it('renders description text', () => {
      render(<FormField><FormDescription>Enter your full name</FormDescription></FormField>)
      expect(screen.getByText('Enter your full name')).toBeInTheDocument()
    })
  })
})
