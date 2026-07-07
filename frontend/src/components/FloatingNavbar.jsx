import { Menu, Moon, PanelLeftClose, Sun } from "lucide-react";

const navItems = ["Dashboard"];

export function FloatingNavbar({ sidebarOpen, onToggleSidebar, darkMode, onToggleDarkMode }) {
  return (
    <header className="fixed left-1/2 top-5 z-40 w-[min(calc(100%-2rem),720px)] -translate-x-1/2">
      <div className="flex h-14 items-center gap-2 rounded-full border border-white/65 bg-white/[0.24] px-3 text-ink shadow-[0_22px_60px_rgba(16,32,51,0.14),inset_0_1px_0_rgba(255,255,255,0.72)] backdrop-blur-2xl backdrop-saturate-150 transition-colors duration-300 dark:border-white/15 dark:bg-[#0d1020]/35 dark:text-white dark:shadow-[0_22px_60px_rgba(0,0,0,0.36),inset_0_1px_0_rgba(255,255,255,0.12)]">
        <button
          type="button"
          onClick={onToggleSidebar}
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-ink/75 transition hover:bg-white/[0.28] hover:text-ink dark:text-white/85 dark:hover:bg-white/10 dark:hover:text-white"
          aria-label={sidebarOpen ? "Collapse sidebar" : "Open sidebar"}
          title={sidebarOpen ? "Collapse sidebar" : "Open sidebar"}
        >
          {sidebarOpen ? <PanelLeftClose size={18} /> : <Menu size={18} />}
        </button>

        <nav className="hidden min-w-0 flex-1 items-center justify-center gap-1 sm:flex">
          {navItems.map((item, index) => (
            <span
              key={item}
              className={
                index === 0
                  ? "rounded-full bg-white/[0.30] px-4 py-2 text-xs font-bold shadow-[inset_0_1px_0_rgba(255,255,255,0.48)] dark:bg-white/[0.10] dark:shadow-[inset_0_1px_0_rgba(255,255,255,0.12)]"
                  : "px-4 py-2 text-xs font-semibold text-ink/70 dark:text-white/72"
              }
            >
              {item}
            </span>
          ))}
        </nav>

        <button
          type="button"
          onClick={onToggleDarkMode}
          className="ml-auto flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-white/40 bg-white/[0.16] text-ink/75 shadow-[inset_0_1px_0_rgba(255,255,255,0.38)] transition hover:bg-white/[0.30] hover:text-ink dark:border-white/10 dark:bg-white/[0.06] dark:text-white/85 dark:shadow-[inset_0_1px_0_rgba(255,255,255,0.10)] dark:hover:bg-white/10 dark:hover:text-white"
          aria-label={darkMode ? "Switch to light mode" : "Switch to dark mode"}
          title={darkMode ? "Light mode" : "Dark mode"}
        >
          {darkMode ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        <div className="shrink-0 rounded-full border border-white/40 bg-white/[0.16] px-4 py-2 text-xs font-black tracking-wide text-ink shadow-[inset_0_1px_0_rgba(255,255,255,0.38)] dark:border-white/10 dark:bg-white/[0.06] dark:text-white dark:shadow-[inset_0_1px_0_rgba(255,255,255,0.10)]">
          Recruitement Agent
        </div>
      </div>
    </header>
  );
}
