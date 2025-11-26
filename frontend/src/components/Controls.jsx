export default function Controls({
  lang,
  setLang,
  understood,
  retry,
  refresh,
  busy,
  onSpeak,
}) {
  return (
    <div className="controls">
      <button className="btn" onClick={retry} disabled={busy}>
        {busy ? '...' : "Didn't get it — explain simpler"}
      </button>
      <button className="btn" onClick={understood} disabled={busy}>
        {busy ? '...' : 'Got it — next topic'}
      </button>
      <span className="lang" />
      <select
        className="btn"
        value={lang}
        onChange={(e) => setLang(e.target.value)}
        disabled={busy}
      >
        <option value="en">Voice: English</option>
        <option value="hi">Voice: Hindi</option>
      </select>
      <button className="btn" onClick={refresh} disabled={busy}>
        {busy ? '...' : 'Refresh Slides'}
      </button>
      <button className="btn" onClick={onSpeak} disabled={busy}>
        🔊 Speak
      </button>
    </div>
  )
}
