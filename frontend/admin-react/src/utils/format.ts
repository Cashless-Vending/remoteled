export const formatCurrency = (cents: number | null | undefined): string => {
  if (cents === null || cents === undefined || isNaN(cents)) {
    return '$0.00'
  }
  return `$${(cents / 100).toFixed(2)}`
}

export const formatDateTime = (dateStr: string): string => {
  return new Date(dateStr).toLocaleString()
}

export const exportToCSV = (data: any[], filename: string) => {
  if (data.length === 0) return

  const headers = Object.keys(data[0])
  const rows = data.map(row => 
    headers.map(header => `"${row[header]}"`)
  )
  
  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.join(','))
  ].join('\n')
  
  const blob = new Blob([csvContent], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

