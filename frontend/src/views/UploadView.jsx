import { motion } from "framer-motion";
import { CheckCircle2, FileText, FileUp, Loader2, Sparkles, Upload } from "lucide-react";
import { useState } from "react";
import { api } from "../api/client.js";
import { Button } from "../components/Button.jsx";
import { SectionShell } from "../components/SectionShell.jsx";
import { useAppState } from "../context/AppState.jsx";

function UploadAction({ accept, onChange, file, label, hint }) {
  return (
    <motion.label
      whileHover={{ y: -2 }}
      className="group flex cursor-pointer items-center justify-between gap-4 rounded-[1.1rem] border border-azure/25 bg-[linear-gradient(180deg,rgba(250,252,255,0.96),rgba(239,246,255,0.92))] px-4 py-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.8)] transition hover:border-azure/50 hover:shadow-[0_16px_30px_rgba(103,170,249,0.14)]"
    >
      <input type="file" accept={accept} onChange={onChange} className="hidden" />
      <div className="flex items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-white text-blush shadow-sm">
          <Upload size={18} />
        </div>
        <div>
          <p className="text-sm font-black text-ink">{label}</p>
          <p className="text-sm text-slate-500">{file?.name || hint}</p>
        </div>
      </div>
      <div className="rounded-full border border-blush/20 bg-white px-3 py-1 text-xs font-bold uppercase tracking-[0.16em] text-blush">
        Browse
      </div>
    </motion.label>
  );
}

function UploadPanel({ icon: Icon, title, subtitle, children }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.24 }}
      className="rounded-[1.4rem] border border-white/80 bg-[linear-gradient(180deg,rgba(255,255,255,0.97),rgba(248,251,255,0.94))] p-6 shadow-[0_25px_60px_rgba(103,170,249,0.12)]"
    >
      <div className="mb-5 flex items-start gap-4">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blush/10 text-blush">
          <Icon size={22} />
        </div>
        <div>
          <h3 className="text-xl font-black text-ink">{title}</h3>
          <p className="mt-1 text-sm text-slate-500">{subtitle}</p>
        </div>
      </div>
      {children}
    </motion.div>
  );
}

export function UploadView() {
  const { resume, setResume, jd, setJD, setActiveSection } = useAppState();
  const [resumeFile, setResumeFile] = useState(null);
  const [jdFile, setJDFile] = useState(null);
  const [jdText, setJDText] = useState("");
  const [loading, setLoading] = useState({ resume: false, jd: false });
  const [error, setError] = useState("");

  async function handleResumeUpload() {
    if (!resumeFile) return;
    setError("");
    setLoading((current) => ({ ...current, resume: true }));
    try {
      const data = await api.uploadResume(resumeFile);
      setResume({ uploaded: true, text: data.resume_text, filename: data.filename, wordCount: data.word_count });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading((current) => ({ ...current, resume: false }));
    }
  }

  async function handleJDUpload() {
    setError("");
    setLoading((current) => ({ ...current, jd: true }));
    try {
      const data = await api.uploadJD({ file: jdFile, text: jdText });
      setJD({ uploaded: true, text: data.jd_text, filename: data.filename || "Pasted JD", wordCount: data.word_count });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading((current) => ({ ...current, jd: false }));
    }
  }

  const ready = resume.uploaded && jd.uploaded;

  return (
    <SectionShell title="Upload Resume + Job Description" kicker="Start here">
      <div className="grid gap-6 lg:grid-cols-2">
        <UploadPanel icon={FileUp} title="Resume PDF" subtitle="Upload the latest version of your resume for parsing and analysis.">
          <UploadAction
            accept="application/pdf"
            file={resumeFile}
            label="Choose resume file"
            hint="PDF only"
            onChange={(event) => setResumeFile(event.target.files?.[0] || null)}
          />
          <Button onClick={handleResumeUpload} disabled={!resumeFile || loading.resume} className="mt-5 min-w-[170px] rounded-2xl">
            {loading.resume && <Loader2 size={16} className="animate-spin" />}
            Process Resume
          </Button>
          {resume.uploaded && (
            <motion.p
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-5 flex items-center gap-2 rounded-xl bg-blush/8 px-3 py-3 text-sm font-semibold text-blush"
            >
              <CheckCircle2 size={18} /> {resume.filename} processed, {resume.wordCount} words
            </motion.p>
          )}
        </UploadPanel>

        <UploadPanel icon={FileText} title="Job Description" subtitle="Upload a JD file or paste the role details to unlock the workflow.">
          <UploadAction
            accept=".txt,.md,application/pdf"
            file={jdFile}
            label="Choose job description file"
            hint="TXT, MD, or PDF"
            onChange={(event) => setJDFile(event.target.files?.[0] || null)}
          />
          <textarea
            value={jdText}
            onChange={(event) => setJDText(event.target.value)}
            rows={8}
            placeholder="Paste the JD here if you do not have a file."
            className="mt-4 w-full resize-y rounded-[1.1rem] border border-slate-200 bg-slate-50/90 p-4 text-sm leading-7 outline-none transition focus:border-azure focus:bg-white"
          />
          <Button onClick={handleJDUpload} disabled={(!jdFile && !jdText.trim()) || loading.jd} className="mt-5 min-w-[150px] rounded-2xl">
            {loading.jd && <Loader2 size={16} className="animate-spin" />}
            Process JD
          </Button>
          {jd.uploaded && (
            <motion.p
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-5 flex items-center gap-2 rounded-xl bg-blush/8 px-3 py-3 text-sm font-semibold text-blush"
            >
              <CheckCircle2 size={18} /> {jd.filename} processed, {jd.wordCount} words
            </motion.p>
          )}
        </UploadPanel>
      </div>

      {error && <div className="mt-5 rounded-lg border border-red-200 bg-red-50 p-4 text-sm font-semibold text-red-700">{error}</div>}

      {ready && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-7 flex items-center justify-between rounded-[1.5rem] border border-electric/20 bg-[linear-gradient(135deg,rgba(240,250,255,0.98),rgba(226,242,255,0.96))] p-6 text-ink shadow-[0_24px_50px_rgba(46,192,249,0.12)]"
        >
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-white text-electric shadow-sm">
              <Sparkles size={24} />
            </div>
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.16em] text-[#328cc2]">Documents ready</p>
              <p className="mt-1 text-xl font-black">Sidebar features are unlocked.</p>
            </div>
          </div>
          <Button onClick={() => setActiveSection("dashboard")} className="rounded-2xl bg-gradient-to-r from-electric to-azure text-white shadow-[0_16px_30px_rgba(46,192,249,0.24)]">
            Open ATS Dashboard
          </Button>
        </motion.div>
      )}
    </SectionShell>
  );
}
