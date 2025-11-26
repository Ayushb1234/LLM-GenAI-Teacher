import { useEffect } from 'react'

export default function ToastStack({ toasts, setToasts }) {
  useEffect(() => {
    if (!toasts.length) return
    const timers = toasts.map((t) =>
      setTimeout(() => {
        setToasts((arr) => arr.filter((x) => x.id !== t.id))
      }, t.ttl ?? 3500)
    )
    return () => timers.forEach(clearTimeout)
  }, [toasts, setToasts])

  return (
    <div className="toast-stack">
      {toasts.map((t) => (
        <div key={t.id} className="toast">{t.msg}</div>
      ))}
    </div>
  )
}
