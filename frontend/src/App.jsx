import { AnimatePresence } from "framer-motion";
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
  const ActiveView = viewMap[activeSection] || UploadView;

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,#c4e0f9_0,#f7fbff_36%,#ffffff_100%)]">
      <Sidebar />
      <main className="ml-72 min-h-screen px-8 py-8">
        <AnimatePresence mode="wait">
          <ActiveView key={activeSection} />
        </AnimatePresence>
      </main>
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
