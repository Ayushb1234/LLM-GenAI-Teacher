import { useCallback, useEffect, useMemo, useState } from 'react'
import TopicSidebar from './components/TopicSidebar.jsx'
import Blackboard from './components/Blackboard.jsx'
import BotAvatar from './components/BotAvatar.jsx'
import Controls from './components/Controls.jsx'
import UploadPanel from './components/UploadPanel.jsx'
import ToastStack from './components/Toast.jsx'
import { nextSlides, sendFeedback } from './lib/api.js'
import useTTS from './hooks/useTTS.js'

export default function App() {
  const [doc, setDoc] = useState(null) // {doc_id, title, plan}
  const [curTopic, setCurTopic] = useState(null)
  const [slides, setSlides] = useState([])
  const [scripts, setScripts] = useState({ en: '', hi: '' })
  const [level, setLevel] = useState(0)
  const [lang, setLang] = useState('en')
  const [busy, setBusy] = useState(false)
  const [toasts, setToasts] = useState([])

  const pushToast = useCallback((msg) => {
    setToasts((arr) => [...arr, { id: Math.random().toString(36).slice(2), msg }])
  }, [])

  const { speak } = useTTS()

  const loadTopic = useCallback(
  async (topic_id, simplify = 0) => {
    if (!doc) return
    setBusy(true)
    try {
      const res = await nextSlides({ doc_id: doc.doc_id, topic_id, simplify_level: simplify })
      setSlides(res.data.slides)
      setScripts({ en: res.data.english_script, hi: res.data.hindi_script })
      setLevel(simplify)
    } catch (err) {
      console.error('teach/next failed', err)
      pushToast('Failed to load slides. Check backend logs.')
    } finally {
      setBusy(false)
    }
  },
  [doc, pushToast]
)


  const understood = useCallback(async () => {
    if (!doc || !curTopic) return
    await sendFeedback({
      doc_id: doc.doc_id,
      topic_id: curTopic,
      understood: true,
      last_simplify_level: level,
    })
    // advance to next topic
    const i = doc.plan.findIndex((p) => p.id === curTopic)
    const nxt = doc.plan[i + 1]?.id
    if (nxt) {
      setCurTopic(nxt)
      await loadTopic(nxt, Math.max(0, level - 1))
    } else {
      pushToast('Course complete 🎉')
    }
  }, [doc, curTopic, level, loadTopic, pushToast])

  const retry = useCallback(async () => {
    if (!doc || !curTopic) return
    await sendFeedback({
      doc_id: doc.doc_id,
      topic_id: curTopic,
      understood: false,
      last_simplify_level: level,
    })
    await loadTopic(curTopic, Math.min(4, level + 1))
  }, [doc, curTopic, level, loadTopic])

  // When doc loads, select first topic
  useEffect(() => {
    if (doc?.plan?.length) setCurTopic(doc.plan[0].id)
  }, [doc])

  // When topic changes, load slides
  useEffect(() => {
    if (curTopic) loadTopic(curTopic, 0)
  }, [curTopic, loadTopic])

  const onSpeak = useCallback(() => {
    const text = lang === 'hi' ? scripts.hi : scripts.en
    if (!text) {
      pushToast('Nothing to speak yet.')
      return
    }
    speak(text, lang)
  }, [lang, scripts, speak, pushToast])

  return (
    <div className="app">
      <TopicSidebar plan={doc?.plan || []} cur={curTopic} setCur={setCurTopic} />
      <div>
        <BotAvatar />

        {!doc && <UploadPanel onReady={setDoc} pushToast={pushToast} />}
        {doc && <div className="small" style={{ marginBottom: 8, opacity: 0.8 }}>
          <b>Document:</b> {doc.title}
        </div>}

        {doc && <Blackboard slides={slides} />}

        <Controls
          lang={lang}
          setLang={setLang}
          understood={understood}
          retry={retry}
          refresh={() => curTopic && loadTopic(curTopic, level)}
          busy={busy}
          onSpeak={onSpeak}
        />

        {scripts.en && (
          <div className="script">
            <div><b>Narration (English text on board)</b></div>
            <div className="small">Switch voice in controls (English/Hindi)</div>
            <p style={{ whiteSpace: 'pre-wrap', marginTop: 8 }}>{scripts.en}</p>
            {scripts.hi && (
              <details style={{ marginTop: 8 }}>
                <summary>Hindi narration (for speech)</summary>
                <p style={{ whiteSpace: 'pre-wrap' }}>{scripts.hi}</p>
              </details>
            )}
          </div>
        )}
      </div>

      <ToastStack toasts={toasts} setToasts={setToasts} />
    </div>
  )
}
