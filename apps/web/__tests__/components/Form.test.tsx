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

  describe('Edge Cases', () => {
    it('FormMessage handles empty error gracefully', () => {
      render(<FormField><FormMessage /></FormField>)
      expect(screen.queryByRole('alert')).not.toBeInTheDocument()
    })

    it('FormLabel does not render without FormField context', () => {
      expect(() => render(<FormLabel>Orphan</FormLabel>)).toThrow()
    })

    it('FormControl renders null children gracefully', () => {
      render(<FormField><FormControl>{null}</FormControl></FormField>)
    })

    it('FormMessage has role="alert"', () => {
      render(<FormField error="Error message"><FormMessage /></FormField>)
      expect(screen.getByRole('alert')).toHaveTextContent('Error message')
    })

    it('FormField renders with long error message', () => {
      const longError = 'E'.repeat(200)
      render(<FormField error={longError}><FormMessage /></FormField>)
      expect(screen.getByRole('alert')).toBeInTheDocument()
      expect(screen.getByText(longError)).toBeInTheDocument()
    })
  })
})
