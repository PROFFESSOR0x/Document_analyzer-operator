import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { ThemeProvider } from '@/components/providers/theme-provider'
import { QueryProvider } from '@/components/providers/query-provider'
import { AuthProvider } from '@/components/providers/auth-provider'
import { Toaster } from '@/components/ui/toast'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Document Analyzer Operator',
  description: 'Multi-agent platform for document analysis, validation, and processing',
  keywords: ['document analyzer', 'AI agents', 'workflow automation', 'knowledge management'],
  authors: [{ name: 'Document Analyzer Team' }],
  creator: 'Document Analyzer Team',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'http://localhost:3000',
    title: 'Document Analyzer Operator',
    description: 'Multi-agent platform for document analysis, validation, and processing',
    siteName: 'Document Analyzer Operator',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Document Analyzer Operator',
    description: 'Multi-agent platform for document analysis, validation, and processing',
  },
  robots: {
    index: false,
    follow: false,
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <QueryProvider>
            <AuthProvider>
              {children}
              <Toaster />
            </AuthProvider>
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
