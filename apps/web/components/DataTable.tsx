import { useMemo, useRef, useState } from 'react'
import { clsx } from 'clsx'
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  flexRender,
  createColumnHelper,
  type ColumnDef as TanstackColumnDef,
  type SortingState,
  type ColumnFiltersState,
  type RowSelectionState,
  type OnChangeFn,
} from '@tanstack/react-table'
import { useVirtualizer } from '@tanstack/react-virtual'
import { ChevronUp, ChevronDown, ChevronsUpDown, ChevronLeft, ChevronRight, Search, Download } from 'lucide-react'
import { Checkbox } from './Checkbox'
import { Button } from '@/components/ui/Button'
import { Skeleton } from '@/components/ui/Skeleton'

interface ColumnDef<T> {
  header: string
  accessorKey?: string
  accessorFn?: (row: T) => unknown
  cell?: (info: { row: T; value: unknown }) => React.ReactNode
  enableSorting?: boolean
  enableFiltering?: boolean
  width?: number | string
  minWidth?: number
  maxWidth?: number
  align?: 'left' | 'center' | 'right'
  hidden?: boolean
  id?: string
}

interface DataTableProps<T> {
  data: T[]
  columns: ColumnDef<T>[]
  enableSelection?: boolean
  enableSorting?: boolean
  enableFiltering?: boolean
  enablePagination?: boolean
  enableColumnResize?: boolean
  enableColumnReorder?: boolean
  enableRowExpansion?: boolean
  enableVirtualScroll?: boolean
  enableExport?: boolean
  pageSize?: number
  pageSizeOptions?: number[]
  stickyFirstColumn?: boolean
  loading?: boolean
  error?: string | null
  emptyState?: {
    icon?: React.ReactNode
    title?: string
    description?: string
    action?: { label: string; onClick: () => void }
  }
  onRowClick?: (row: T) => void
  onSelectionChange?: (selectedRows: T[]) => void
  renderExpandedRow?: (row: T) => React.ReactNode
  variant?: 'table' | 'datagrid'
  className?: string
}

function DataTable<T extends { id?: string }>({
  data,
  columns: rawColumns,
  enableSelection = false,
  enableSorting = true,
  enableFiltering = false,
  enablePagination = true,
  enableColumnResize = false,
  enableColumnReorder = false,
  enableRowExpansion = false,
  enableVirtualScroll = false,
  enableExport = false,
  pageSize = 10,
  pageSizeOptions = [5, 10, 20, 50],
  stickyFirstColumn = false,
  loading = false,
  error: tableError = null,
  emptyState,
  onRowClick,
  onSelectionChange,
  renderExpandedRow,
  variant = 'table',
  className,
}: DataTableProps<T>) {
  const [sorting, setSorting] = useState<SortingState>([])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
  const [globalFilter, setGlobalFilter] = useState('')
  const [rowSelection, setRowSelection] = useState<RowSelectionState>({})
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set())
  const tableContainerRef = useRef<HTMLDivElement>(null)

  const columns = useMemo(() => {
    const result: TanstackColumnDef<T>[] = []

    if (enableSelection) {
      result.push({
        id: 'select',
        header: ({ table }) => (
          <Checkbox
            checked={table.getIsAllRowsSelected()}
            indeterminate={table.getIsSomeRowsSelected()}
            onChange={(checked) => table.toggleAllRowsSelected(checked)}
            size="sm"
            aria-label="Select all rows"
          />
        ),
        cell: ({ row }) => (
          <Checkbox
            checked={row.getIsSelected()}
            onChange={(checked) => row.toggleSelected(checked)}
            size="sm"
            aria-label={`Select row ${row.id}`}
          />
        ),
        size: 44,
        enableSorting: false,
        enableColumnFilter: false,
      })
    }

    if (enableRowExpansion) {
      result.push({
        id: 'expand',
        header: '',
        cell: ({ row }) => {
          const rowId = String(row.id)
          const isExpanded = expandedRows.has(rowId)
          return (
            <button
              onClick={() => {
                const next = new Set(expandedRows)
                isExpanded ? next.delete(rowId) : next.add(rowId)
                setExpandedRows(next)
              }}
              className="p-1 text-text-secondary hover:text-text-primary transition-colors"
              aria-label={isExpanded ? 'Collapse row' : 'Expand row'}
              aria-expanded={isExpanded}
            >
              <ChevronRight
                className={clsx(
                  'h-4 w-4 transition-transform',
                  isExpanded && 'rotate-90'
                )}
              />
            </button>
          )
        },
        size: 44,
        enableSorting: false,
        enableColumnFilter: false,
      })
    }

    for (const col of rawColumns) {
      if (col.hidden) continue
      result.push({
        id: col.id || col.accessorKey,
        header: col.header,
        accessorKey: col.accessorKey as any,
        accessorFn: col.accessorFn,
        cell: col.cell
          ? (info) => col.cell!({ row: info.row.original, value: info.getValue() })
          : undefined,
        enableSorting: col.enableSorting ?? enableSorting,
        enableColumnFilter: col.enableFiltering ?? enableFiltering,
        size: typeof col.width === 'number' ? col.width : undefined,
        minSize: col.minWidth,
        maxSize: col.maxWidth,
        meta: { align: col.align },
      } as TanstackColumnDef<T>)
    }

    return result
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [rawColumns, enableSelection, enableRowExpansion, enableSorting, enableFiltering])

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      columnFilters,
      globalFilter,
      rowSelection,
    },
    enableRowSelection: enableSelection,
    onRowSelectionChange: (updater) => {
      const next = typeof updater === 'function' ? updater(rowSelection) : updater
      setRowSelection(next)
      if (onSelectionChange) {
        const selected = data.filter((_, i) => next[i])
        onSelectionChange(selected)
      }
    },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: enablePagination ? getPaginationRowModel() : undefined,
    getRowId: (row) => (row as any).id ?? String(data.indexOf(row)),
  })

  const { rows } = table.getRowModel()
  const rowVirtualizer = useVirtualizer(
    enableVirtualScroll
      ? {
          count: rows.length,
          getScrollElement: () => tableContainerRef.current,
          estimateSize: () => 52,
          overscan: 10,
        }
      : { count: 0, getScrollElement: () => null, estimateSize: () => 52, enabled: false }
  )

  const handleExportCSV = () => {
    const headers = rawColumns.filter((c) => !c.hidden).map((c) => c.header)
    const csvRows = data.map((row) =>
      rawColumns
        .filter((c) => !c.hidden)
        .map((col) => {
          const val = col.accessorFn
            ? col.accessorFn(row)
            : col.accessorKey
              ? (row as any)[col.accessorKey]
              : ''
          return JSON.stringify(String(val ?? ''))
        })
        .join(',')
    )
    const csv = [headers.join(','), ...csvRows].join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'export.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  if (tableError) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-4">
        <div className="w-16 h-16 rounded-full bg-accent-error/10 flex items-center justify-center">
          <span className="text-accent-error text-2xl font-bold">!</span>
        </div>
        <p className="text-text-primary font-display text-lg">{tableError}</p>
        <Button variant="outline" onClick={() => window.location.reload()}>
          Retry
        </Button>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="space-y-3">
        <div className="flex items-center gap-4 px-4 py-3">
          {columns.map((_, i) => (
            <Skeleton key={i} className="h-4 flex-1" />
          ))}
        </div>
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="flex items-center gap-4 px-4 py-3">
            {columns.map((_, j) => (
              <Skeleton key={j} className={clsx('h-3 flex-1', j > 2 && 'hidden lg:block')} />
            ))}
          </div>
        ))}
      </div>
    )
  }

  if (!rows.length) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-4" role="status">
        {emptyState?.icon || (
          <div className="w-16 h-16 rounded-full bg-background-elevated flex items-center justify-center">
                            <svg className="w-8 h-8 text-text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
                    </div>
        )}
        <p className="text-text-primary font-display text-lg">
          {emptyState?.title || 'No data'}
        </p>
        {emptyState?.description && (
          <p className="text-text-secondary text-sm max-w-md text-center">
            {emptyState.description}
          </p>
        )}
        {emptyState?.action && (
          <Button variant="primary" onClick={emptyState.action.onClick}>
            {emptyState.action.label}
          </Button>
        )}
      </div>
    )
  }

  const renderSortIcon = (header: any) => {
    if (!header.column.getCanSort()) return null
    const sorted = header.column.getIsSorted()
    if (sorted === 'asc') return <ChevronUp className="h-3.5 w-3.5 text-accent-primary ml-1" />
    if (sorted === 'desc') return <ChevronDown className="h-3.5 w-3.5 text-accent-primary ml-1" />
    return <ChevronsUpDown className="h-3.5 w-3.5 text-text-tertiary ml-1 opacity-0 group-hover:opacity-100 transition-opacity" />
  }

  return (
    <div className={clsx('w-full', className)}>
      {(enableFiltering || enableExport) && (
        <div className="flex items-center justify-between mb-4 gap-4">
          {enableFiltering && (
            <div className="relative flex-1 max-w-xs">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-tertiary" />
              <input
                value={globalFilter}
                onChange={(e) => setGlobalFilter(e.target.value)}
                placeholder="Search..."
                className="w-full bg-background-dark border border-border rounded-lg pl-10 pr-4 py-2 text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:border-accent-primary transition-colors"
                aria-label="Search table"
              />
            </div>
          )}
          {enableExport && (
            <Button variant="ghost" size="sm" onClick={handleExportCSV}>
              <Download className="h-4 w-4 mr-1.5" />
              Export CSV
            </Button>
          )}
        </div>
      )}

      <div className="overflow-x-auto rounded-xl border border-border" ref={tableContainerRef}>
        <table
          className="w-full border-collapse"
          role={variant === 'datagrid' ? 'grid' : 'table'}
          aria-busy={loading}
        >
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className={clsx(
                      'h-11 px-4 text-left text-table-header text-text-secondary bg-background-card border-b border-border-subtle font-semibold',
                      header.column.getCanSort() && 'cursor-pointer select-none group',
                      stickyFirstColumn && header.column.getIsFirstColumn() && 'sticky left-0 z-10 bg-background-card',
                      { 'text-center': (header.column.columnDef.meta as any)?.align === 'center' },
                      { 'text-right': (header.column.columnDef.meta as any)?.align === 'right' }
                    )}
                    onClick={header.column.getToggleSortingHandler()}
                    scope="col"
                    aria-sort={
                      header.column.getIsSorted()
                        ? header.column.getIsSorted() === 'asc'
                          ? 'ascending'
                          : 'descending'
                        : 'none'
                    }
                    style={{
                      width: header.getSize() !== 150 ? header.getSize() : undefined,
                      minWidth: header.column.columnDef.minSize,
                      maxWidth: header.column.columnDef.maxSize,
                    }}
                  >
                    <div className="flex items-center">
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      {renderSortIcon(header)}
                    </div>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {(enableVirtualScroll ? rowVirtualizer.getVirtualItems() : rows).map((virtualRow: any, i: number) => {
              const row = enableVirtualScroll ? rows[virtualRow.index] : (virtualRow as typeof rows[0])
              const isExpanded = expandedRows.has(String(row.id))
              const isSelected = row.getIsSelected()

              return (
                <tr
                  key={row.id}
                  className={clsx(
                    'h-13 border-b border-border-subtle transition-colors',
                    i % 2 === 0 ? 'bg-transparent' : 'bg-background-card',
                    isSelected && 'bg-accent-primary/5 shadow-[inset_3px_0_0] shadow-accent-primary',
                    onRowClick && 'cursor-pointer hover:bg-background-elevated/50'
                  )}
                  onClick={() => onRowClick?.(row.original)}
                  aria-selected={isSelected || undefined}
                >
                  {row.getVisibleCells().map((cell) => (
                    <td
                      key={cell.id}
                      className={clsx(
                        'px-4 py-3 text-table-cell text-text-primary',
                        stickyFirstColumn && cell.column.getIsFirstColumn() && 'sticky left-0 z-10 bg-inherit',
                        { 'text-center': (cell.column.columnDef.meta as any)?.align === 'center' },
                        { 'text-right': (cell.column.columnDef.meta as any)?.align === 'right' }
                      )}
                    >
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {enablePagination && (
        <div className="flex items-center justify-between mt-4 gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm text-text-secondary">
              {table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1}–
              {Math.min(
                (table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize,
                data.length
              )}{' '}
              of {data.length}
            </span>
            <select
              value={table.getState().pagination.pageSize}
              onChange={(e) => table.setPageSize(Number(e.target.value))}
              className="bg-background-dark border border-border rounded-lg px-2 py-1 text-sm text-text-primary"
              aria-label="Rows per page"
            >
              {pageSizeOptions.map((opt) => (
                <option key={opt} value={opt}>
                  {opt} / page
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={() => table.setPageIndex(0)}
              disabled={!table.getCanPreviousPage()}
              className="h-9 w-9 flex items-center justify-center rounded-lg text-sm text-text-secondary hover:text-text-primary hover:bg-background-elevated disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              aria-label="First page"
            >
              <ChevronLeft className="h-4 w-4" />
              <ChevronLeft className="h-4 w-4 -ml-2" />
            </button>
            <button
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
              className="h-9 w-9 flex items-center justify-center rounded-lg text-sm text-text-secondary hover:text-text-primary hover:bg-background-elevated disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              aria-label="Previous page"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>

            {generatePageNumbers(
              table.getState().pagination.pageIndex,
              table.getPageCount()
            ).map((page, i) =>
              page === '...' ? (
                <span key={`ellipsis-${i}`} className="h-9 w-9 flex items-center justify-center text-text-tertiary">
                  ...
                </span>
              ) : (
                <button
                  key={page}
                  onClick={() => table.setPageIndex(page as number)}
                  className={clsx(
                    'h-9 min-w-[36px] px-2 flex items-center justify-center rounded-lg text-sm transition-colors',
                    table.getState().pagination.pageIndex === page
                      ? 'bg-accent-primary text-white'
                      : 'text-text-secondary hover:text-text-primary hover:bg-background-elevated'
                  )}
                  aria-current={table.getState().pagination.pageIndex === page ? 'page' : undefined}
                >
                  {(page as number) + 1}
                </button>
              )
            )}

            <button
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
              className="h-9 w-9 flex items-center justify-center rounded-lg text-sm text-text-secondary hover:text-text-primary hover:bg-background-elevated disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              aria-label="Next page"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
            <button
              onClick={() => table.setPageIndex(table.getPageCount() - 1)}
              disabled={!table.getCanNextPage()}
              className="h-9 w-9 flex items-center justify-center rounded-lg text-sm text-text-secondary hover:text-text-primary hover:bg-background-elevated disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              aria-label="Last page"
            >
              <ChevronRight className="h-4 w-4" />
              <ChevronRight className="h-4 w-4 -ml-2" />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

function generatePageNumbers(current: number, total: number): (number | '...')[] {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i)

  const pages: (number | '...')[] = [0]
  if (current > 2) pages.push('...')

  const start = Math.max(1, current - 1)
  const end = Math.min(total - 2, current + 1)
  for (let i = start; i <= end; i++) pages.push(i)

  if (current < total - 3) pages.push('...')
  pages.push(total - 1)

  return pages
}

export { DataTable }
export type { DataTableProps, ColumnDef }
