const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8001";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json") ? await response.json() : await response.text();

  if (!response.ok) {
    const message = typeof payload === "string" ? payload : payload.detail || "Request failed";
    throw new Error(message);
  }

  return payload;
}

function jsonPost(path, body) {
  return request(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export const api = {
  uploadResume(file) {
    const formData = new FormData();
    formData.append("file", file);
    return request("/api/upload/resume", { method: "POST", body: formData });
  },
  uploadJD({ file, text }) {
    const formData = new FormData();
    if (file) formData.append("file", file);
    if (text) formData.append("jd_text", text);
    return request("/api/upload/jd", { method: "POST", body: formData });
  },
  runATS(resumeText, jdText) {
    return jsonPost("/api/ats", { resume_text: resumeText, jd_text: jdText });
  },
  analyzeResume(resumeText) {
    return jsonPost("/api/resume-analysis", { resume_text: resumeText });
  },
  coverLetter(resumeText, jdText) {
    return jsonPost("/api/cover-letter", { resume_text: resumeText, jd_text: jdText });
  },
  interviewQuestions(resumeText, jdText) {
    return jsonPost("/api/interview-questions", { resume_text: resumeText, jd_text: jdText });
  },
  roadmap(missingSkills) {
    return jsonPost("/api/roadmap", { missing_skills: missingSkills });
  },
  chat({ query, resumeText, jdText, missingSkills }) {
    return jsonPost("/api/chat", {
      query,
      resume_text: resumeText,
      jd_text: jdText,
      missing_skills: missingSkills,
    });
  },
  previewRecruiters(file, resumeSkills) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("resume_skills", Array.isArray(resumeSkills) ? resumeSkills.join(",") : "");
    return request("/api/cold-email/preview", { method: "POST", body: formData });
  },
  sendColdEmails(payload) {
    return jsonPost("/api/cold-email/send", payload);
  },
};
