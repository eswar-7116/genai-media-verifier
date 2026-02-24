"use client"

import { usePathname } from 'next/navigation'
import { LearnNavigationPill } from "@/components/ui/learn-navigation-pill"

export default function ConditionalLearnNav() {
  const pathname = usePathname()
  
  if (pathname !== '/learn') {
    return null
  }
  
  return (
    <>
      <div className="fixed top-6 left-8 z-50">
        <img src="/new-logo.jpeg" alt="Logo" className="h-10 w-auto object-contain drop-shadow-lg" />
      </div>
      <div className="fixed top-6 left-0 right-0 z-50 flex justify-center pointer-events-none">
        <LearnNavigationPill />
      </div>
    </>
  )
}
