'use client'

import { useState, useMemo, forwardRef, type HTMLAttributes } from 'react'
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  flexRender,
  type ColumnDef,
  type SortingState,
  type ColumnFiltersState,
  type Table as TableType,
} from '@tanstack/react-table'
import { ChevronUp, ChevronDown, ChevronsUpDown, ChevronLeft, ChevronRight } from 'lucide-react'
import { cn } from './utils'

interface DataTableProps<T> extends Omit<HTMLAttributes<HTMLDivElement>, 'children'> {
  columns: ColumnDef<T>[]
  data: T[]
  pageSize?: number
  searchable?: boolean
  searchPlaceholder?: string
  onRowClick?: (row: T) => void
}

const DataTable = forwardRef<HTMLDivElement, DataTableProps<unknown>>(
  (
    {
      columns,
      data: rawData,
      pageSize = 10,
      searchable = false,
      searchPlaceholder = 'Search...',
      onRowClick,
      className,
      ...props
    },
    ref,
  ) => {
    const [sorting, setSorting] = useState<SortingState>([])
    const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
    const [globalFilter, setGlobalFilter] = useState('')
    const [pagination, setPagination] = useState({ pageIndex: 0, pageSize })

    const data = useMemo(() => rawData, [rawData])

    const table = useReactTable({
      data,
      columns,
      state: {
        sorting,
        columnFilters,
        globalFilter,
        pagination,
      },
      onSortingChange: setSorting,
      onColumnFiltersChange: setColumnFilters,
      onGlobalFilterChange: setGlobalFilter,
      onPaginationChange: setPagination,
      getCoreRowModel: getCoreRowModel(),
      getSortedRowModel: getSortedRowModel(),
      getFilteredRowModel: getFilteredRowModel(),
      getPaginationRowModel: getPaginationRowModel(),
    })

    const totalRows = table.getFilteredRowModel().rows.length
    const pageCount = table.getPageCount()
    const pageIndex = pagination.pageIndex
    const startRow = pageIndex * pageSize + 1
    const endRow = Math.min((pageIndex + 1) * pageSize, totalRows)

    return (
      <div ref={ref} className={cn('w-full', className)} data-slot="data-table" {...props}>
        {searchable && (
          <div className="mb-4">
            <input
              type="text"
              value={globalFilter}
              onChange={(e) => {
                setGlobalFilter(e.target.value)
                setPagination((prev) => ({ ...prev, pageIndex: 0 }))
              }}
              placeholder={searchPlaceholder}
              className={cn(
                'h-9 w-full max-w-sm rounded-lg border border-border bg-background-card px-3 text-sm text-text-primary',
                'placeholder:text-text-tertiary',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2 focus-visible:ring-offset-background',
                'transition-colors',
              )}
              aria-label="Search table"
              autoComplete="off"
            />
          </div>
        )}

        <div className="overflow-x-auto rounded-lg border border-border">
          <table role="table" className="w-full border-collapse text-sm">
            <thead>
              {table.getHeaderGroups().map((headerGroup) => (
                <tr key={headerGroup.id} className="border-b border-border">
                  {headerGroup.headers.map((header) => {
                    const canSort = header.column.getCanSort()
                    const isSorted = header.column.getIsSorted()

                    return (
                      <th
                        key={header.id}
                        className={cn(
                          'h-10 px-4 text-left text-xs font-medium uppercase tracking-wider text-text-tertiary',
                          canSort && [
                            'cursor-pointer select-none',
                            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-[var(--ring)]',
                          ],
                          isSorted && 'text-accent-primary',
                        )}
                        onClick={header.column.getToggleSortingHandler()}
                        tabIndex={canSort ? 0 : undefined}
                        aria-sort={
                          isSorted === 'asc'
                            ? 'ascending'
                            : isSorted === 'desc'
                              ? 'descending'
                              : undefined
                        }
                      >
                        <div className="flex items-center gap-1.5">
                          {flexRender(header.column.columnDef.header, header.getContext())}
                          {canSort && (
                            <span className="shrink-0" aria-hidden="true">
                              {isSorted === 'asc' ? (
                                <ChevronUp className="size-3.5" />
                              ) : isSorted === 'desc' ? (
                                <ChevronDown className="size-3.5" />
                              ) : (
                                <ChevronsUpDown className="size-3.5 text-text-tertiary/50" />
                              )}
                            </span>
                          )}
                        </div>
                      </th>
                    )
                  })}
                </tr>
              ))}
            </thead>
            <tbody>
              {table.getRowModel().rows.length === 0 ? (
                <tr>
                  <td
                    colSpan={columns.length}
                    className="px-4 py-12 text-center text-sm text-text-tertiary"
                  >
                    No results found
                  </td>
                </tr>
              ) : (
                table.getRowModel().rows.map((row) => (
                  <tr
                    key={row.id}
                    className={cn(
                      'border-b border-border transition-colors last:border-b-0',
                      onRowClick && 'cursor-pointer',
                      'hover:bg-background-elevated',
                    )}
                    onClick={() => onRowClick?.(row.original)}
                    tabIndex={onRowClick ? 0 : undefined}
                    onKeyDown={
                      onRowClick
                        ? (e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                              e.preventDefault()
                              onRowClick(row.original)
                            }
                          }
                        : undefined
                    }
                    role={onRowClick ? 'button' : undefined}
                  >
                    {row.getVisibleCells().map((cell) => (
                      <td key={cell.id} className="px-4 py-3 text-text-primary">
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {totalRows > 0 && (
          <div className="flex items-center justify-between px-1 py-3 text-sm text-text-secondary">
            <span>
              {startRow}-{endRow} of {totalRows}
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => table.previousPage()}
                disabled={!table.getCanPreviousPage()}
                className={cn(
                  'inline-flex size-8 items-center justify-center rounded-lg border border-border transition-colors',
                  'hover:bg-background-elevated',
                  'disabled:pointer-events-none disabled:opacity-40',
                  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2 focus-visible:ring-offset-background',
                )}
                aria-label="Previous page"
              >
                <ChevronLeft className="size-4" aria-hidden="true" />
              </button>
              <span className="min-w-[5rem] text-center text-xs text-text-tertiary">
                Page {pageIndex + 1} of {pageCount || 1}
              </span>
              <button
                onClick={() => table.nextPage()}
                disabled={!table.getCanNextPage()}
                className={cn(
                  'inline-flex size-8 items-center justify-center rounded-lg border border-border transition-colors',
                  'hover:bg-background-elevated',
                  'disabled:pointer-events-none disabled:opacity-40',
                  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2 focus-visible:ring-offset-background',
                )}
                aria-label="Next page"
              >
                <ChevronRight className="size-4" aria-hidden="true" />
              </button>
            </div>
          </div>
        )}
      </div>
    )
  },
)

DataTable.displayName = 'DataTable'

export { DataTable }
export type { DataTableProps }
