export const SERVICE_TYPE_CODES = [
  {
    value: 'TRIGGER',
    label: 'Trigger',
    helper: 'One-time activation (no duration fields).'
  },
  {
    value: 'FIXED',
    label: 'Fixed Duration',
    helper: 'Requires fixed_minutes; no variable pricing.'
  },
  {
    value: 'VARIABLE',
    label: 'Variable Duration',
    helper: 'Requires minutes_per_25c; priced by usage.'
  }
]

export const MAX_SERVICE_TYPE_COUNT = SERVICE_TYPE_CODES.length


