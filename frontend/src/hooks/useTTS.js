import { useEffect, useRef } from 'react'

export default function useTTS() {
  const voicesRef = useRef([])
  const readyRef = useRef(false)

  const refreshVoices = () => {
    const vs = window.speechSynthesis?.getVoices?.() || []
    voicesRef.current = vs
    readyRef.current = true
  }

  useEffect(() => {
    if (!('speechSynthesis' in window)) return
    refreshVoices()
    const handler = () => refreshVoices()
    window.speechSynthesis.addEventListener('voiceschanged', handler)
    return () => {
      window.speechSynthesis.removeEventListener('voiceschanged', handler)
      window.speechSynthesis.cancel()
    }
  }, [])

  const pick = (voices, code) =>
    voices.find((v) => v.lang?.toLowerCase().startsWith(code))

  const speak = async (text, lang = 'en') => {
    if (!text) return
    // Try browser voice first
    if ('speechSynthesis' in window) {
      const utter = new SpeechSynthesisUtterance(text)
      const vs = voicesRef.current
      const voice =
        lang === 'hi'
          ? pick(vs, 'hi') || pick(vs, 'mr') || null
          : pick(vs, 'en') || null
      if (voice) {
        utter.voice = voice
        utter.lang = lang === 'hi' ? 'hi-IN' : 'en-US'
        window.speechSynthesis.cancel()
        window.speechSynthesis.speak(utter)
        return
      }
    }
    // Fallback: server TTS
    const base = (import.meta.env.VITE_API_BASE || 'http://localhost:8000').replace(/\/+$/, '')
    const url = `${base}/tts?lang=${encodeURIComponent(lang)}&text=${encodeURIComponent(text)}`
    const audio = new Audio(url)
    audio.play().catch(() => {
      alert('Could not play TTS audio')
    })
  }

  return { speak, ttsReady: readyRef.current }
}
