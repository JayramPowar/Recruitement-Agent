import { motion } from "framer-motion";
import {
  Bot,
  Check,
  FileQuestion,
  FileText,
  Gauge,
  Lock,
  Mail,
  Map,
  X,
  PenLine,
  UploadCloud,
} from "lucide-react";
import logoDark from "../assets/resumelens-mark-dark.png";
import logoLight from "../assets/resumelens-mark-light.png";
import { useAppState } from "../context/AppState.jsx";

export const sections = [
  { id: "upload", label: "Upload Resume + JD", icon: UploadCloud, locked: false },
  { id: "dashboard", label: "ATS Dashboard", icon: Gauge, locked: true },
  { id: "resume", label: "Resume Analysis", icon: FileText, locked: true },
  { id: "cover", label: "Cover Letter", icon: PenLine, locked: true },
  { id: "interview", label: "Interview Questions", icon: FileQuestion, locked: true },
  { id: "roadmap", label: "Learning Roadmap", icon: Map, locked: true },
  { id: "email", label: "Cold Email Sender", icon: Mail, locked: true },
  { id: "chat", label: "AI Chatbot", icon: Bot, locked: true },
];

function StatusPill({ label, done }) {
  return (
    <div className="flex items-center justify-between rounded-lg bg-white/70 px-3 py-2 text-sm text-ink shadow-sm dark:bg-white/[0.08] dark:text-slate-100">
      <span>{label}</span>
      <span className={done ? "text-blush" : "text-slate-400"}>{done ? <Check size={16} /> : <Lock size={15} />}</span>
    </div>
  );
}

export function Sidebar({ open, onClose, darkMode }) {
  const { activeSection, setActiveSection, resume, jd, isReady } = useAppState();
  const logoSrc = darkMode ? logoDark : logoLight;

  return (
    <motion.aside
      initial={false}
      animate={{ x: open ? 0 : "-100%" }}
      transition={{ duration: 0.24, ease: "easeOut" }}
      className="fixed left-0 top-0 z-30 flex h-screen w-72 flex-col border-r border-azure/20 bg-ice/85 p-5 pt-20 shadow-[18px_0_55px_rgba(16,32,51,0.12)] backdrop-blur-xl dark:border-white/10 dark:!bg-[linear-gradient(180deg,rgba(13,18,30,0.98),rgba(9,13,23,0.96))] dark:shadow-[18px_0_55px_rgba(0,0,0,0.35)]"
    >
      <div className="mb-6 rounded-2xl border border-white/70 bg-white/80 p-3 shadow-sm dark:border-white/10 dark:bg-[#081121]/80">
        <div className="flex items-center gap-3">
          <img src={logoSrc} alt="" className="h-16 w-16 shrink-0 rounded-xl object-cover" />
          <div className="min-w-0">
            <div className="text-2xl font-black leading-none text-ink dark:text-white">
              Resume<span className="text-blush dark:text-[#f36aa8]">Lens</span>
            </div>
            <p className="mt-1 text-xs font-semibold text-slate-500 dark:text-slate-400">See Your Best. Get Hired.</p>
          </div>
        </div>
      </div>

      <div className="mb-5 flex items-center justify-between">
        <div>
          <div className="text-xs font-bold uppercase tracking-[0.2em] text-blush dark:text-[#f3a6c4]">Workspace</div>
          <p className="mt-1 text-sm font-semibold text-slate-600 dark:text-slate-300">Navigation</p>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="flex h-9 w-9 items-center justify-center rounded-full bg-white/70 text-ink shadow-sm transition hover:bg-white dark:bg-white/[0.08] dark:text-white dark:hover:bg-white/[0.15]"
          aria-label="Dismiss sidebar"
          title="Dismiss sidebar"
        >
          <X size={17} />
        </button>
      </div>

      <div className="mb-6 space-y-2">
        <StatusPill label="Resume" done={resume.uploaded} />
        <StatusPill label="Job Description" done={jd.uploaded} />
      </div>

      <nav className="space-y-2">
        {sections.map((item) => {
          const Icon = item.icon;
          const locked = item.locked && !isReady;
          const active = activeSection === item.id;

          return (
            <motion.button
              key={item.id}
              type="button"
              onClick={() => !locked && setActiveSection(item.id)}
              disabled={locked}
              animate={{ opacity: locked ? 0.38 : 1, filter: locked ? "grayscale(0.9)" : "grayscale(0)" }}
              transition={{ duration: 0.2 }}
              whileHover={!locked ? { scale: 1.02 } : undefined}
              className={`flex w-full items-center gap-3 rounded-lg px-3 py-3 text-left text-sm font-semibold transition ${
                active
                  ? "bg-blush text-white shadow-soft dark:bg-[#d36a98]"
                  : "bg-white/55 text-ink hover:bg-white hover:shadow-md dark:bg-white/[0.08] dark:text-slate-100 dark:hover:bg-white/[0.12]"
              } ${locked ? "pointer-events-none cursor-not-allowed" : ""}`}
            >
              <Icon size={18} />
              <span className="flex-1">{item.label}</span>
              {locked && <Lock size={15} />}
            </motion.button>
          );
        })}
      </nav>

      <div className="mt-auto rounded-lg border border-white/70 bg-white/55 p-3 text-xs leading-relaxed text-slate-600 dark:border-white/10 dark:bg-white/[0.08] dark:text-slate-300">
        Locked sections open after both documents are processed by the backend.
      </div>
    </motion.aside>
  );
}
