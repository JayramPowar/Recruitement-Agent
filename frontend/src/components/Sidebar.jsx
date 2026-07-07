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
  PenLine,
  UploadCloud,
} from "lucide-react";
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
    <div className="flex items-center justify-between rounded-lg bg-white/70 px-3 py-2 text-sm text-ink shadow-sm">
      <span>{label}</span>
      <span className={done ? "text-blush" : "text-slate-400"}>{done ? <Check size={16} /> : <Lock size={15} />}</span>
    </div>
  );
}

export function Sidebar() {
  const { activeSection, setActiveSection, resume, jd, isReady } = useAppState();

  return (
    <aside className="fixed left-0 top-0 z-20 flex h-screen w-72 flex-col border-r border-azure/20 bg-ice/80 p-5 backdrop-blur-xl">
      <div className="mb-7">
        <div className="text-xs font-bold uppercase tracking-[0.2em] text-blush">AI Recruitment</div>
        <h1 className="mt-2 text-2xl font-black leading-tight text-ink">Copilot</h1>
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
                  ? "bg-blush text-white shadow-soft"
                  : "bg-white/55 text-ink hover:bg-white hover:shadow-md"
              } ${locked ? "pointer-events-none cursor-not-allowed" : ""}`}
            >
              <Icon size={18} />
              <span className="flex-1">{item.label}</span>
              {locked && <Lock size={15} />}
            </motion.button>
          );
        })}
      </nav>

      <div className="mt-auto rounded-lg border border-white/70 bg-white/55 p-3 text-xs leading-relaxed text-slate-600">
        Locked sections open after both documents are processed by the backend.
      </div>
    </aside>
  );
}
