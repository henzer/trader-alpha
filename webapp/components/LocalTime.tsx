'use client'

export default function LocalTime({ date }: { date: string }) {
  const formattedDate = new Date(date).toLocaleString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })

  return <span>{formattedDate}</span>
}