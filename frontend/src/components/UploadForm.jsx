import { useState } from "react";
import { uploadResumes } from "../api";


export default function UploadForm({ onUploadComplete }) {
  const [jobTitle, setJobTitle] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (files.length === 0) {
      setError("Please select at least one resume PDF.");
      return;
    }
    if (!jobDescription.trim()) {
      setError("Please paste the job description.");
      return;
    }

    setLoading(true);
    try {
      const data = await uploadResumes(files, jobDescription, jobTitle);
      onUploadComplete(data.results);
      setFiles([]);
    } catch (err) {
      setError(err?.response?.data?.detail || "Something went wrong while uploading.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h2>1. Upload Resumes &amp; Job Description</h2>

      <label className="field-label">Job Title</label>
      <input
        type="text"
        placeholder="e.g. Backend Python Developer"
        value={jobTitle}
        onChange={(e) => setJobTitle(e.target.value)}
      />

      <label className="field-label">Job Description</label>
      <textarea
        rows={6}
        placeholder="Paste the full job description here..."
        value={jobDescription}
        onChange={(e) => setJobDescription(e.target.value)}
      />

      <label className="field-label">Resume PDF(s)</label>
      <input
        type="file"
        accept="application/pdf"
        multiple
        onChange={(e) => setFiles(Array.from(e.target.files))}
      />
      {files.length > 0 && (
        <p className="hint">{files.length} file(s) selected</p>
      )}

      {error && <p className="error">{error}</p>}

      <button type="submit" disabled={loading}>
        {loading ? "Analyzing..." : "Analyze Resumes"}
      </button>
    </form>
  );
}
