import { createContext, useContext, useMemo, useState } from "react";

const AppStateContext = createContext(null);

export function AppStateProvider({ children }) {
  const [resume, setResume] = useState({ uploaded: false, text: "", filename: "", wordCount: 0 });
  const [jd, setJD] = useState({ uploaded: false, text: "", filename: "", wordCount: 0 });
  const [ats, setATS] = useState(null);
  const [resumeSkills, setResumeSkills] = useState([]);
  const [activeSection, setActiveSection] = useState("upload");

  const value = useMemo(() => {
    const isReady = resume.uploaded && jd.uploaded;
    return {
      resume,
      setResume,
      jd,
      setJD,
      ats,
      setATS,
      resumeSkills,
      setResumeSkills,
      activeSection,
      setActiveSection,
      isReady,
    };
  }, [resume, jd, ats, resumeSkills, activeSection]);

  return <AppStateContext.Provider value={value}>{children}</AppStateContext.Provider>;
}

export function useAppState() {
  const context = useContext(AppStateContext);
  if (!context) {
    throw new Error("useAppState must be used inside AppStateProvider");
  }
  return context;
}
