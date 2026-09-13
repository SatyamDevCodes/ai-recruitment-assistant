import axios from "axios";

const BASE_URL = "http://localhost:8000";

// 1. Resumes + Job Description upload karna
export async function uploadResumes(files, jobDescription, jobTitle) {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }
  formData.append("job_description", jobDescription);
  formData.append("job_title", jobTitle || "Untitled Role");

  const response = await axios.post(`${BASE_URL}/api/upload-resume`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

// 2. Saare candidates ki list lana 
export async function getCandidates() {
  const response = await axios.get(`${BASE_URL}/api/candidates`);
  return response.data.candidates;
}

// 3. AI assistant se natural language me question poochna
export async function askQuestion(question) {
  const response = await axios.post(`${BASE_URL}/api/ask`, { question });
  return response.data.answer;
}
