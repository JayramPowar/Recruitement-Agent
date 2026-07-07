import { AnimatePresence } from "framer-motion";
import { useState } from "react";
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
        <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <main className={`min-h-screen px-5 pb-8 pt-28 transition-[margin] duration-300 sm:px-8 ${sidebarOpen ? "lg:ml-72" : "lg:ml-0"}`}>
          <AnimatePresence mode="wait">
            <ActiveView key={activeSection} />
          </AnimatePresence>
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
