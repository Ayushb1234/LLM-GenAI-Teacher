import { useState } from 'react'
import { ingestPdf, getPlan } from '../lib/api'

export default function UploadPanel({ onReady, pushToast }) {
  const [busy, setBusy] = useState(false)

  const onChange = async (e) => {
    const f = e.target.files?.[0]
    if (!f) return
    if (f.type !== 'application/pdf' && !f.name.toLowerCase().endsWith('.pdf')) {
      pushToast('Please upload a PDF file.')
      return
    }

    setBusy(true)
    try {
      const up = await ingestPdf(f)
      const { doc_id, title } = up.data
      const plan = await getPlan(doc_id)
      onReady({ doc_id, title, plan: plan.data.plan })
      pushToast(`Ingested: ${title}`)
    } catch (err) {
      console.error(err)
      pushToast('Upload failed. Check backend is running and CORS is allowed.')
    } finally {
      setBusy(false)
      // reset the input so same file can be re-selected if needed
      e.target.value = ''
    }
  }

  return (
    <div className="upload">
      <p><b>Upload subject PDF</b></p>
      <input type="file" accept="application/pdf" onChange={onChange} disabled={busy} />
      {busy && (
        <p className="small">
          <span className="spinner" /> Processing… extracting topics, building index…
        </p>
      )}
      <p className="small" style={{ opacity: 0.75, marginTop: 6 }}>
        Pro tip: clean, text-based PDFs parse best.
      </p>
    </div>
  )
}
