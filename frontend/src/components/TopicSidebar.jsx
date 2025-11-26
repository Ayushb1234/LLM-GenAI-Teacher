export default function TopicSidebar({ plan, cur, setCur }) {
  return (
    <div className="sidebar">
      <h3>Topics</h3>
      {plan?.map((t) => (
        <div
          key={t.id}
          className={`topic ${cur === t.id ? 'active' : ''}`}
          onClick={() => setCur(t.id)}
        >
          <div className="row">
            <b style={{ flex: 1 }}>{t.title}</b>
            <span className="small">~{t.est_minutes}m</span>
          </div>
        </div>
      ))}
      {!plan?.length && (
        <div className="small" style={{ opacity: 0.8, marginTop: 8 }}>
          Upload a PDF to generate a plan.
        </div>
      )}
    </div>
  )
}
