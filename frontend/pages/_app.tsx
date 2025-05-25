import '../styles/globals.css'
import type { AppProps } from 'next/app'
import { useEffect } from 'react'

export default function App({ Component, pageProps }: AppProps) {
  useEffect(() => {
    // Check if backend is running
    const checkBackend = async () => {
      try {
        const response = await fetch('/api/health')
        if (!response.ok) {
          console.warn('Backend server not responding')
        }
      } catch (error) {
        console.warn('Backend connection failed:', error)
      }
    }
    
    checkBackend()
  }, [])

  return <Component {...pageProps} />
}
