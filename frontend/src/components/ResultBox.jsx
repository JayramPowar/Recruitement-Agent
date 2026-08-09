import { CheckCircle2, AlertTriangle, Lightbulb, Gauge } from "lucide-react";

function formatInline(text) {
  const safeText = typeof text === "string" ? text : String(text ?? "");
  const segments = safeText.split(/(\*\*.*?\*\*)/g).filter(Boolean);
  return segments.map((segment, index) => {
    if (segment.startsWith("**") && segment.endsWith("**")) {
      return (
        <strong key={`${segment}-${index}`} className="font-bold text-ink dark:text-white">
          {segment.slice(2, -2)}
        </strong>
      );
    }
    return <span key={`${segment}-${index}`}>{segment}</span>;
  });
}

// Parse raw text into { title, description, bullets }[] sections
function parseSections(content) {
  const safeContent = typeof content === "string" ? content : String(content ?? "");
  const lines = safeContent.split("\n").map((l) => l.trim()).filter(Boolean);
  const sections = [];
  let current = null;

  for (const line of lines) {
    const headingMatch = line.match(/^\d+\.\s+(.*)$/);
    if (headingMatch) {
      const headingText = headingMatch[1].trim();
      const [titlePart, ...descriptionParts] = headingText.split(/:\s*/);
      const title = titlePart.replace(/:$/, "");
      const description = descriptionParts.length ? descriptionParts.join(": ") : null;
      current = { title, description, bullets: [] };
      sections.push(current);
      continue;
    }
    const bulletMatch = line.match(/^[-*]\s+(.*)$/);
    if (bulletMatch) {
      if (!current) sections.push((current = { title: null, description: null, bullets: [] }));
      current.bullets.push(bulletMatch[1]);
      continue;
    }
    if (current) {
      if (current.bullets.length) {
        current.bullets[current.bullets.length - 1] += " " + line;
      } else if (current.description) {
        current.description += " " + line;
      } else {
        current.description = line;
      }
    } else {
      current = { title: null, description: line, bullets: [] };
      sections.push(current);
    }
  }
  if (!sections.length && safeContent.trim()) {
    return [{ title: null, description: safeContent, bullets: [] }];
  }
  return sections;
}

function parseParagraphs(content) {
  const safeContent = typeof content === "string" ? content : String(content ?? "");
  return safeContent
    .split(/\n\s*\n/)
    .map((paragraph) => paragraph.trim())
    .filter(Boolean);
}

function parseRoadmapWeeks(content) {
  const safeContent = typeof content === "string" ? content : String(content ?? "");
  const lines = safeContent.split("\n").map((line) => line.trim()).filter(Boolean);
  const weeks = [];
  let currentWeek = null;

  for (const line of lines) {
    const weekMatch = line.match(/^Week\s+(\d+)\s*:\s*(.*)$/i);
    if (weekMatch) {
      currentWeek = {
        title: `Week ${weekMatch[1]}`,
        subtitle: weekMatch[2]?.trim() || "",
        items: [],
      };
      weeks.push(currentWeek);
      continue;
    }

    if (!currentWeek) {
      currentWeek = { title: "", subtitle: "", items: [] };
      weeks.push(currentWeek);
    }

    currentWeek.items.push(line);
  }

  return weeks;
}

// Decide icon/color treatment based on the section title
function getSectionStyle(title = "") {
  const t = String(title ?? "").toLowerCase();
  if (t.includes("strength") && !t.includes("overall")) {
    return {
      icon: CheckCircle2,
      iconColor: "text-emerald-600 dark:text-emerald-400",
      bg: "bg-emerald-50 dark:bg-emerald-500/10",
      border: "border-emerald-200 dark:border-emerald-500/20",
    };
  }
  if (t.includes("weakness")) {
    return {
      icon: AlertTriangle,
      iconColor: "text-amber-600 dark:text-amber-400",
      bg: "bg-amber-50 dark:bg-amber-500/10",
      border: "border-amber-200 dark:border-amber-500/20",
    };
  }
  if (t.includes("suggestion") || t.includes("improve")) {
    return {
      icon: Lightbulb,
      iconColor: "text-sky-600 dark:text-sky-400",
      bg: "bg-sky-50 dark:bg-sky-500/10",
      border: "border-sky-200 dark:border-sky-500/20",
    };
  }
  return null; // neutral / score section handled separately
}

function ScoreBadge({ description }) {
  const scoreMatch = description?.match(/(\d+(\.\d+)?)\s*\/\s*10/);
  const score = scoreMatch ? parseFloat(scoreMatch[1]) : null;

  return (
    <div className="flex items-center gap-4 rounded-2xl border border-blush/20 bg-[linear-gradient(135deg,rgba(236,72,153,0.08),rgba(103,170,249,0.08))] p-5 dark:border-white/10">
      <div className="flex h-16 w-16 shrink-0 flex-col items-center justify-center rounded-full bg-white shadow-sm dark:bg-slate-800">
        <Gauge className="mb-0.5 h-4 w-4 text-blush" />
        <span className="text-lg font-black leading-none text-ink dark:text-white">
          {score !== null ? score : "—"}
        </span>
      </div>
      <div>
        <p className="text-xs font-bold uppercase tracking-wide text-blush">Overall Strength</p>
        <p className="text-sm font-semibold text-ink dark:text-white">
          {score !== null ? `${score} / 10` : description}
        </p>
      </div>
    </div>
  );
}

function Section({ section }) {
  const style = getSectionStyle(section.title);
  const titleText = String(section.title ?? "");
  const descriptionText = String(section.description ?? "");
  const bullets = Array.isArray(section.bullets) ? section.bullets.filter(Boolean) : [];

  // Score section gets the special badge treatment
  if (titleText.toLowerCase().includes("overall strength")) {
    return <ScoreBadge description={descriptionText} />;
  }

  // Plain description-only section (e.g. "Score justification")
  if (!style && descriptionText && !bullets.length) {
    return (
      <div>
        {titleText && (
          <h3 className="mb-1.5 text-sm font-bold text-ink dark:text-white">
            {formatInline(titleText)}
          </h3>
        )}
        <p className="text-sm leading-6 text-slate-600 dark:text-slate-300">{formatInline(descriptionText)}</p>
      </div>
    );
  }

  const Icon = style?.icon;

  return (
    <div className={`rounded-xl border p-4 ${style?.border ?? "border-slate-200 dark:border-white/10"} ${style?.bg ?? ""}`}>
      <div className="mb-3 flex items-center gap-2">
        {Icon && <Icon className={`h-4 w-4 ${style.iconColor}`} strokeWidth={2.5} />}
        {titleText && <h3 className="text-sm font-bold text-ink dark:text-white">{formatInline(titleText)}</h3>}
      </div>

      {descriptionText && <p className="mb-2 text-sm leading-6 text-slate-600 dark:text-slate-300">{formatInline(descriptionText)}</p>}

      {bullets.length > 0 && (
        <ul className="space-y-2">
          {bullets.map((item, i) => (
            <li key={i} className="flex gap-2 text-sm leading-6 text-slate-700 dark:text-slate-200">
              <span className={`mt-2 h-1 w-1 shrink-0 rounded-full ${style?.iconColor ?? "bg-slate-400"} bg-current`} />
              <span>{formatInline(item)}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function CoverLetterBox({ content }) {
  const paragraphs = parseParagraphs(content);

  return (
    <div className="space-y-5">
      {paragraphs.map((paragraph, index) => (
        <p key={index} className="text-[15px] leading-8 text-slate-700 dark:text-slate-200">
          {formatInline(paragraph)}
        </p>
      ))}
    </div>
  );
}

function RoadmapBox({ content }) {
  const weeks = parseRoadmapWeeks(content);

  return (
    <div className="space-y-4">
      {weeks.map((week, index) => (
        <div key={`${week.title}-${index}`} className="rounded-xl border border-slate-200 p-5 dark:border-white/10">
          {(week.title || week.subtitle) && (
            <div className="mb-3">
              {week.title && <h3 className="text-lg font-black text-ink dark:text-white">{week.title}</h3>}
              {week.subtitle && <p className="mt-1 text-sm font-semibold text-slate-800 dark:text-slate-200">{formatInline(week.subtitle)}</p>}
            </div>
          )}
          <div className="space-y-2">
            {week.items.map((item, itemIndex) => {
              const isBullet = /^[-*]\s+/.test(item);
              const cleanItem = item.replace(/^[-*]\s+/, "");
              const isLabel = /^(focus area|topics|activities|project|checkpoint|deliverable)\s*:/i.test(cleanItem);

              if (isBullet) {
                return (
                  <div key={itemIndex} className="flex gap-2 text-sm leading-7 text-slate-700 dark:text-slate-200">
                    <span className="mt-3 h-1.5 w-1.5 shrink-0 rounded-full bg-slate-800 dark:bg-slate-200" />
                    <span>{formatInline(cleanItem)}</span>
                  </div>
                );
              }

              return (
                <p key={itemIndex} className={`text-sm leading-7 ${isLabel ? "font-semibold text-ink dark:text-white" : "text-slate-700 dark:text-slate-200"}`}>
                  {formatInline(cleanItem)}
                </p>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}

export function ResultBox({ children, className = "", variant = "default" }) {
  const content = typeof children === "string" ? children : String(children ?? "");
  const sections = parseSections(content);

  return (
    <div
      className={`rounded-[1.25rem] border border-white/70 bg-[linear-gradient(145deg,rgba(255,255,255,0.98),rgba(244,249,255,0.96))] p-6 shadow-[0_22px_50px_rgba(103,170,249,0.12)] dark:border-white/10 dark:!bg-[linear-gradient(145deg,rgba(26,32,46,0.98),rgba(16,22,35,0.96))] dark:shadow-[0_22px_50px_rgba(0,0,0,0.22)] ${className}`}
    >
      {variant === "cover-letter" ? (
        <CoverLetterBox content={content} />
      ) : variant === "roadmap" ? (
        <RoadmapBox content={content} />
      ) : (
        <div className="space-y-4">
          {sections.map((section, i) => (
            <Section key={i} section={section} />
          ))}
        </div>
      )}
    </div>
  );
}
