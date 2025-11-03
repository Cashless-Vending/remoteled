import { formatDateTime } from '../../utils/format'
import type { SystemLog } from '../../types'

interface LogsTableProps {
  logs: SystemLog[]
  onRefresh: () => void
  loading?: boolean
  error?: string | null
}

export const LogsTable = ({ logs, onRefresh, loading = false, error = null }: LogsTableProps) => {
  return (
    <div className="card">
      <div className="card-header">
        <div>
          <div className="card-title">System Logs</div>
          <p style={{ fontSize: '0.85rem', color: '#718096' }}>Recent device communication events</p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={onRefresh} disabled={loading}>
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {error ? (
        <div style={{ padding: '1rem', color: '#c53030', fontSize: '0.9rem' }}>
          {error}
        </div>
      ) : null}

      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Device</th>
            <th>Direction</th>
            <th>Status</th>
            <th>Details</th>
          </tr>
        </thead>
        <tbody>
          {logs.length === 0 ? (
            <tr>
              <td colSpan={5} style={{ textAlign: 'center', padding: '2rem', color: '#718096' }}>
                No log entries yet.
              </td>
            </tr>
          ) : (
            logs.map(log => (
              <tr key={log.id}>
                <td>{formatDateTime(log.created_at)}</td>
                <td>{log.device_label}</td>
                <td>
                  <span className={`badge ${log.direction === 'OUT' ? 'RUNNING' : 'INFO'}`}>
                    {log.direction}
                  </span>
                </td>
                <td>
                  <span className={`badge ${log.ok ? 'ACTIVE' : 'OFFLINE'}`}>
                    {log.ok ? 'OK' : 'Error'}
                  </span>
                </td>
                <td>{log.details}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}


