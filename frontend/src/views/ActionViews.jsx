import { motion } from "framer-motion";
import { Loader2, Send, Sparkles } from "lucide-react";
import { useState } from "react";
import { api } from "../api/client.js";
import { Button } from "../components/Button.jsx";
import { ResultBox } from "../components/ResultBox.jsx";
import { SectionShell } from "../components/SectionShell.jsx";
import { useAppState } from "../context/AppState.jsx";

function GeneratedView({ title, kicker, buttonLabel, run, resultKey }) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState("");
  const [error, setError] = useState("");

  async function handleRun() {
    setError("");
    setLoading(true);
    try {
      const data = await run();
      setResult(data[resultKey]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <SectionShell title={title} kicker={kicker}>
      <motion.div
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-[1.4rem] bg-[linear-gradient(180deg,rgba(255,255,255,0.98),rgba(246,250,255,0.94))] p-6 shadow-[0_24px_60px_rgba(103,170,249,0.12)]"
      >
        <div className="mb-5 flex items-center justify-between gap-4 rounded-[1.2rem] border border-ice/80 bg-[linear-gradient(135deg,rgba(244,250,255,0.95),rgba(234,244,255,0.95))] px-5 py-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.14em] text-blush">{kicker}</p>
            <p className="mt-1 text-sm text-slate-600">Run the existing backend workflow and render the answer in a cleaner reading view.</p>
          </div>
          <div className="hidden h-11 w-11 items-center justify-center rounded-2xl bg-white text-electric shadow-sm sm:flex">
            <Sparkles size={20} />
          </div>
        </div>
        <Button onClick={handleRun} disabled={loading} className="rounded-2xl">
          {loading && <Loader2 size={16} className="animate-spin" />}
          {buttonLabel}
        </Button>
        {error && <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm font-semibold text-red-700">{error}</div>}
        {result && <ResultBox className="mt-4">{result}</ResultBox>}
      </motion.div>
    </SectionShell>
  );
}

export function ResumeAnalysisView() {
  const { resume } = useAppState();
  return (
    <GeneratedView
      title="Resume Analysis"
      kicker="AI review"
      buttonLabel="Analyze My Resume"
      run={() => api.analyzeResume(resume.text)}
      resultKey="analysis"
    />
  );
}

export function CoverLetterView() {
  const { resume, jd } = useAppState();
  return (
    <GeneratedView
      title="Cover Letter Generator"
      kicker="Personalized draft"
      buttonLabel="Generate Cover Letter"
      run={() => api.coverLetter(resume.text, jd.text)}
      resultKey="cover_letter"
    />
  );
}

export function InterviewView() {
  const { resume, jd } = useAppState();
  return (
    <GeneratedView
      title="Interview Questions"
      kicker="Preparation"
      buttonLabel="Generate Questions"
      run={() => api.interviewQuestions(resume.text, jd.text)}
      resultKey="questions"
    />
  );
}

export function RoadmapView() {
  const { ats } = useAppState();
  const missingSkills = ats?.missing_skills || [];
  return (
    <GeneratedView
      title="Learning Roadmap"
      kicker="Skill plan"
      buttonLabel="Generate Roadmap"
      run={() => api.roadmap(missingSkills)}
      resultKey="roadmap"
    />
  );
}

export function ChatView() {
  const { resume, jd, ats } = useAppState();
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function ask() {
    setError("");
    setLoading(true);
    try {
      const data = await api.chat({
        query,
        resumeText: resume.text,
        jdText: jd.text,
        missingSkills: ats?.missing_skills || [],
      });
      setAnswer(data.answer);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <SectionShell title="AI Career Chatbot" kicker="Ask anything">
      <motion.div
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-[1.4rem] bg-[linear-gradient(180deg,rgba(255,255,255,0.98),rgba(246,250,255,0.94))] p-6 shadow-[0_24px_60px_rgba(103,170,249,0.12)]"
      >
        <textarea
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          rows={4}
          className="w-full rounded-[1.2rem] border border-slate-200 bg-slate-50/90 p-4 leading-7 outline-none transition focus:border-azure focus:bg-white"
          placeholder="Ask about your resume, JD fit, missing skills, or interview preparation."
        />
        <Button onClick={ask} disabled={!query.trim() || loading} className="mt-4 rounded-2xl">
          {loading ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
          Ask
        </Button>
        {error && <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm font-semibold text-red-700">{error}</div>}
        {answer && <ResultBox className="mt-4">{answer}</ResultBox>}
      </motion.div>
    </SectionShell>
  );
}

export function ColdEmailView() {
  const { resumeSkills } = useAppState();
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [senderEmail, setSenderEmail] = useState("");
  const [appPassword, setAppPassword] = useState("");
  const [delay, setDelay] = useState(30);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState("");
  const [error, setError] = useState("");

  async function loadPreview() {
    setError("");
    setLoading("preview");
    try {
      setPreview(await api.previewRecruiters(file, resumeSkills));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading("");
    }
  }

  async function sendEmails() {
    setError("");
    setLoading("send");
    try {
      const data = await api.sendColdEmails({ sender_email: senderEmail, app_password: appPassword, resume_skills: resumeSkills, delay });
      setResults(data.results);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading("");
    }
  }

  return (
    <SectionShell title="Cold Email Sender" kicker="Recruiter outreach">
      <div className="grid gap-5 lg:grid-cols-[1fr_1.2fr]">
        <div className="rounded-lg bg-white p-5 shadow-sm">
          <input type="file" accept=".xlsx" onChange={(event) => setFile(event.target.files?.[0] || null)} className="w-full rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm" />
          <Button onClick={loadPreview} disabled={!file || loading === "preview"} className="mt-4">
            {loading === "preview" && <Loader2 size={16} className="animate-spin" />}
            Preview Recruiters
          </Button>
          <input value={senderEmail} onChange={(event) => setSenderEmail(event.target.value)} placeholder="Your Gmail" className="mt-5 w-full rounded-lg border border-slate-200 bg-slate-50 p-3 outline-none focus:border-azure" />
          <input value={appPassword} onChange={(event) => setAppPassword(event.target.value)} placeholder="Gmail app password" type="password" className="mt-3 w-full rounded-lg border border-slate-200 bg-slate-50 p-3 outline-none focus:border-azure" />
          <label className="mt-3 block text-sm font-semibold text-slate-600">Delay: {delay}s</label>
          <input type="range" min="10" max="60" value={delay} onChange={(event) => setDelay(Number(event.target.value))} className="w-full accent-blush" />
          <Button onClick={sendEmails} disabled={!preview || !senderEmail || !appPassword || loading === "send"} className="mt-4">
            {loading === "send" && <Loader2 size={16} className="animate-spin" />}
            Send Emails
          </Button>
          {error && <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm font-semibold text-red-700">{error}</div>}
        </div>
        <div className="space-y-4">
          {preview && (
            <div className="rounded-lg bg-white p-5 shadow-sm">
              <h3 className="font-black">Found {preview.count} recruiters</h3>
              <ResultBox className="mt-3 max-h-72 overflow-auto">{preview.preview}</ResultBox>
            </div>
          )}
          {results.length > 0 && <ResultBox>{results.map((item) => `${item.status} - ${item.hr_name} | ${item.company} | ${item.email}`).join("\n")}</ResultBox>}
        </div>
      </div>
    </SectionShell>
  );
}
