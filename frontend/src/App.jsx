import { useEffect, useState } from "react";
import UploadForm from "./components/UploadForm";
import CandidateTable from "./components/CandidateTable";
import AskAssistant from "./components/AskAssistant";
import { getCandidates } from "./api";


function App() {
  const [candidates, setCandidates] = useState([]);

  async function refreshCandidates() {
    try {
      const data = await getCandidates();
      setCandidates(data);
    } catch (err) {
      console.error("Failed to fetch candidates", err);
    }
  }

  useEffect(() => {
    refreshCandidates();
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <h1>AI Recruitment Assistant</h1>
        <p>Upload resumes, get instant AI-powered candidate analysis, and ask questions in plain English.</p>
      </header>

      <UploadForm onUploadComplete={refreshCandidates} />
      <CandidateTable candidates={candidates} />
      <AskAssistant />
    </div>
  );
}

export default App;
