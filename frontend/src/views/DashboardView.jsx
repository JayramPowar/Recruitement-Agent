import { Loader2, Play } from "lucide-react";
import { useState } from "react";
import { api } from "../api/client.js";
import { Button } from "../components/Button.jsx";
import { SectionShell } from "../components/SectionShell.jsx";
import { useAppState } from "../context/AppState.jsx";

function Metric({ label, value }) {
  return (
    <div className="rounded-lg border border-azure/20 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-[#151c2b]">
      <p className="text-sm font-semibold text-slate-500 dark:text-slate-400">{label}</p>
      <p className="mt-2 text-3xl font-black text-ink dark:text-white">{value}</p>
    </div>
  );
}

export function DashboardView() {
  const { resume, jd, ats, setATS, setResumeSkills } = useAppState();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const matchedSkills = Array.isArray(ats?.matched_skills) ? ats.matched_skills : [];
  const missingSkills = Array.isArray(ats?.missing_skills) ? ats.missing_skills : [];
  const formatIssues = Array.isArray(ats?.format_issues) ? ats.format_issues : [];
  const formatSuggestions = Array.isArray(ats?.format_suggestions) ? ats.format_suggestions : [];

  async function runATS() {
    setError("");
    setLoading(true);
    try {
      const data = await api.runATS(resume.text, jd.text);
      setATS(data.result);
      setResumeSkills(data.resume_skills || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <SectionShell title="ATS Dashboard" kicker="Match analysis">
      <div className="mb-5 flex items-center justify-between rounded-lg bg-white p-5 shadow-sm dark:bg-[#151c2b]">
        <div>
          <p className="text-sm font-semibold text-slate-500 dark:text-slate-400">Full ATS Analysis</p>
          <p className="mt-1 text-slate-700 dark:text-slate-200">Scores keywords, matching skills, experience, education, and format.</p>
        </div>
        <Button onClick={runATS} disabled={loading}>
          {loading ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
          Run Analysis
        </Button>
      </div>

      {error && <div className="mb-5 rounded-lg border border-red-200 bg-red-50 p-4 text-sm font-semibold text-red-700">{error}</div>}

      {ats && (
        <div className="space-y-5">
          <div className="grid gap-4 md:grid-cols-5">
            <Metric label="Final Score" value={`${ats.ats_score}%`} />
            <Metric label="Keywords" value={`${ats.keyword_score}%`} />
            <Metric label="Semantic" value={`${ats.semantic_score}%`} />
            <Metric label="Experience" value={`${ats.experience_score}%`} />
            <Metric label="Education" value={`${ats.education_score}%`} />
          </div>

          <div className="grid gap-5 lg:grid-cols-2">
            <div className="rounded-lg bg-white p-5 shadow-sm dark:bg-[#151c2b]">
              <h3 className="font-black dark:text-white">Matched Skills</h3>
              <div className="mt-3 flex flex-wrap gap-2">
                {matchedSkills.map((skill) => (
                  <span key={skill} className="rounded-full bg-ice px-3 py-1 text-sm font-semibold text-ink dark:bg-electric/20 dark:text-slate-100">{skill}</span>
                ))}
                {matchedSkills.length === 0 && <p className="text-sm text-slate-500 dark:text-slate-400">No matched skills found yet.</p>}
              </div>
            </div>
            <div className="rounded-lg bg-white p-5 shadow-sm dark:bg-[#151c2b]">
              <h3 className="font-black dark:text-white">Missing Skills</h3>
              <div className="mt-3 flex flex-wrap gap-2">
                {missingSkills.map((skill) => (
                  <span key={skill} className="rounded-full bg-blush/10 px-3 py-1 text-sm font-semibold text-blush dark:bg-blush/20 dark:text-[#f3a6c4]">{skill}</span>
                ))}
                {missingSkills.length === 0 && <p className="text-sm text-slate-500 dark:text-slate-400">No missing skills detected.</p>}
              </div>
            </div>
          </div>

          <div className="rounded-lg bg-white p-5 shadow-sm dark:bg-[#151c2b]">
            <h3 className="font-black dark:text-white">Format Check</h3>
            <div className="mt-3 space-y-2 text-sm text-slate-700 dark:text-slate-200">
              {formatIssues.map((issue) => <p key={issue}>{issue}</p>)}
              {formatSuggestions.map((suggestion) => <p key={suggestion} className="font-semibold text-blush dark:text-[#f3a6c4]">{suggestion}</p>)}
              {!formatIssues.length && !formatSuggestions.length && <p className="text-slate-500 dark:text-slate-400">Run ATS analysis to see formatting feedback.</p>}
            </div>
          </div>
        </div>
      )}
    </SectionShell>
  );
}
