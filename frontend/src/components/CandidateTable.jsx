export default function CandidateTable({ candidates }) {
  if (!candidates || candidates.length === 0) {
    return (
      <div className="card">
        <h2>2. Candidates</h2>
        <p className="hint">No candidates yet. Upload resumes above to get started.</p>
      </div>
    );
  }

  function badgeClass(recommendation) {
    if (recommendation === "Shortlist") return "badge badge-green";
    if (recommendation === "Consider") return "badge badge-yellow";
    return "badge badge-red";
  }

  return (
    <div className="card">
      <h2>2. Candidates ({candidates.length})</h2>
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Experience</th>
              <th>Score</th>
              <th>Matching Skills</th>
              <th>Missing Skills</th>
              <th>Recommendation</th>
            </tr>
          </thead>
          <tbody>
            {candidates.map((c) => (
              <tr key={c.id}>
                <td>{c.name || "—"}</td>
                <td>{c.email || "—"}</td>
                <td>{c.experience_years != null ? `${c.experience_years} yrs` : "—"}</td>
                <td className="score-cell">{c.match_score != null ? Math.round(c.match_score) : "—"}</td>
                <td>{c.matching_skills || "—"}</td>
                <td>{c.missing_skills || "—"}</td>
                <td>
                  <span className={badgeClass(c.recommendation)}>
                    {c.recommendation || "—"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
