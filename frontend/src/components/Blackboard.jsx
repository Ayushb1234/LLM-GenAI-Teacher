export default function Blackboard({ slides }) {
  if (!slides?.length)
    return (
      <div className="board">
        <div className="inner">Upload a PDF and pick a topic.</div>
      </div>
    )

  return (
    <div className="board">
      <div className="inner">
        {slides.map((s, i) => (
          <section key={i} style={{ marginBottom: 20 }}>
            <h2 className="heading">{s.heading}</h2>
            {(s.bullets || []).map((b, j) => (
              <div key={j} className="bullet">
                {b}
              </div>
            ))}
            {s.example && (
              <div className="bullet">
                <i>Example:</i> {s.example}
              </div>
            )}
          </section>
        ))}
      </div>
    </div>
  )
}
