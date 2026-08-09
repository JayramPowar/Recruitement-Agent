import { AnimatePresence } from "framer-motion";
import React, { useState } from "react";
import { FloatingNavbar } from "./components/FloatingNavbar.jsx";
import { Sidebar } from "./components/Sidebar.jsx";
import { AppStateProvider, useAppState } from "./context/AppState.jsx";
import { DashboardView } from "./views/DashboardView.jsx";
import {
  ChatView,
  ColdEmailView,
  CoverLetterView,
  InterviewView,
  ResumeAnalysisView,
  RoadmapView,
} from "./views/ActionViews.jsx";
import { UploadView } from "./views/UploadView.jsx";

const viewMap = {
  upload: UploadView,
  dashboard: DashboardView,
  resume: ResumeAnalysisView,
  cover: CoverLetterView,
  interview: InterviewView,
  roadmap: RoadmapView,
  email: ColdEmailView,
  chat: ChatView,
};

class AppErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, message: "" };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, message: error?.message || "Something went wrong while rendering this screen." };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="mx-auto mt-24 max-w-3xl rounded-[1.4rem] border border-red-200 bg-white p-8 shadow-[0_24px_60px_rgba(103,170,249,0.12)] dark:border-red-400/30 dark:bg-[#151c2b]">
          <p className="text-sm font-semibold uppercase tracking-[0.14em] text-red-600 dark:text-red-300">Screen error</p>
          <h2 className="mt-2 text-2xl font-black text-ink dark:text-white">This page hit a rendering error.</h2>
          <p className="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-300">{this.state.message}</p>
        </div>
      );
    }

    return this.props.children;
  }
}

function AppContent() {
  const { activeSection } = useAppState();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const ActiveView = viewMap[activeSection] || UploadView;

  return (
    <div className={darkMode ? "dark" : ""}>
      <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,#c4e0f9_0,#f7fbff_36%,#ffffff_100%)] transition-colors duration-300 dark:bg-[radial-gradient(circle_at_top_left,#233552_0,#111827_42%,#090b12_100%)]">
        <FloatingNavbar
          sidebarOpen={sidebarOpen}
          onToggleSidebar={() => setSidebarOpen((current) => !current)}
          darkMode={darkMode}
          onToggleDarkMode={() => setDarkMode((current) => !current)}
        />
        <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} darkMode={darkMode} />
        <main className={`min-h-screen px-5 pb-8 pt-28 transition-[margin] duration-300 sm:px-8 ${sidebarOpen ? "lg:ml-72" : "lg:ml-0"}`}>
          <AppErrorBoundary key={activeSection}>
            <AnimatePresence mode="wait">
              <ActiveView key={activeSection} />
            </AnimatePresence>
          </AppErrorBoundary>
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AppStateProvider>
      <AppContent />
    </AppStateProvider>
  );
}
