import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AI Recruitment System',
  description: 'Intelligent job-resume matching powered by BERT & RoBERTa',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

