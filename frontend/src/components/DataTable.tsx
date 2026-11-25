import type { ReactNode } from 'react'

import { LoadingState } from './LoadingState'

export interface DataTableColumn<T> {
  key: string
  header: string
  render: (row: T) => ReactNode
  headerClassName?: string
  cellClassName?: string
}

interface DataTableProps<T> {
  columns: DataTableColumn<T>[]
  rows: T[]
  rowKey: (row: T) => string
  caption?: string
  loading?: boolean
  loadingLabel?: string
  empty?: ReactNode
  compact?: boolean
}

export function DataTable<T>({
  columns,
  rows,
  rowKey,
  caption,
  loading = false,
  loadingLabel,
  empty = null,
  compact = false,
}: DataTableProps<T>) {
  if (loading) {
    return <LoadingState label={loadingLabel} compact={compact} />
  }

  if (rows.length === 0) {
    return <>{empty}</>
  }

  return (
    <div className="table-wrap">
      <table className={compact ? 'compact-table' : undefined}>
        {caption && <caption className="sr-only">{caption}</caption>}
        <thead>
          <tr>
            {columns.map((column) => (
              <th
                key={column.key}
                scope="col"
                className={column.headerClassName}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={rowKey(row)}>
              {columns.map((column) => (
                <td key={column.key} className={column.cellClassName}>
                  {column.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
