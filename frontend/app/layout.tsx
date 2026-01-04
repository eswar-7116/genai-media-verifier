import type { Metadata } from 'next'
import { Geist, Geist_Mono, Space_Grotesk } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import './globals.css'
import { PillBase } from "@/components/ui/3d-adaptive-navigation-bar"

const geist = Geist({ subsets: ["latin"], variable: '--font-geist' });
const geistMono = Geist_Mono({ subsets: ["latin"], variable: '--font-geist-mono' });
const spaceGrotesk = Space_Grotesk({ subsets: ["latin"], variable: '--font-space' });

export const metadata: Metadata = {
  title: 'V.E.R.I.T.A.S - AI Media Credibility Analysis',
  description: 'AI-assisted media credibility analysis',
  icons: {
    icon: [
      {
        url: '/icon-light-32x32.png',
        media: '(prefers-color-scheme: light)',
      },
      {
        url: '/icon-dark-32x32.png',
        media: '(prefers-color-scheme: dark)',
      },
      {
        url: '/icon.svg',
        type: 'image/svg+xml',
      },
    ],
    apple: '/apple-icon.png',
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={`${geist.variable} ${geistMono.variable} ${spaceGrotesk.variable} font-sans antialiased`} suppressHydrationWarning>
        <div className="fixed top-6 left-8 z-50">
          <img src="/logo.png" alt="Logo" className="h-10 w-auto object-contain drop-shadow-lg" />
        </div>
        <div className="fixed top-6 left-0 right-0 z-50 flex justify-center pointer-events-none">
          <PillBase />
        </div>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
