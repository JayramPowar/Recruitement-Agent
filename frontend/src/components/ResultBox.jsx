function formatInline(text) {
  const segments = text.split(/(\*\*.*?\*\*)/g).filter(Boolean);

  return segments.map((segment, index) => {
    if (segment.startsWith("**") && segment.endsWith("**")) {
      return (
        <strong key={`${segment}-${index}`} className="font-black text-ink">
          {segment.slice(2, -2)}
        </strong>
      );
    }

    return <span key={`${segment}-${index}`}>{segment}</span>;
  });
}

function renderStructuredContent(content) {
  const lines = content.split("\n").map((line) => line.trimEnd());
  const blocks = [];
  let listItems = [];
  let listType = null;

  function flushList() {
    if (!listItems.length) return;
    const isOrdered = listType === "ordered";
    const ListTag = isOrdered ? "ol" : "ul";

    blocks.push(
      <ListTag key={`list-${blocks.length}`} className={`space-y-3 pl-6 ${isOrdered ? "" : "list-disc marker:text-blush"}`}>
        {listItems.map((item, index) => (
          <li
            key={`${item}-${index}`}
            className={isOrdered ? "list-decimal marker:font-black marker:text-blush" : ""}
          >
            <span className="text-slate-700">{formatInline(item)}</span>
          </li>
        ))}
      </ListTag>
    );
    listItems = [];
    listType = null;
  }

  lines.forEach((line, index) => {
    const trimmed = line.trim();

    if (!trimmed) {
      flushList();
      return;
    }

    const headingMatch = trimmed.match(/^###\s+(.*)$/);
    if (headingMatch) {
      flushList();
      blocks.push(
        <h3 key={`h3-${index}`} className="pt-1 text-lg font-black text-ink">
          {formatInline(headingMatch[1])}
        </h3>
      );
      return;
    }

    const listMatch = trimmed.match(/^\d+\.\s+(.*)$/);
    if (listMatch) {
      if (listType && listType !== "ordered") {
        flushList();
      }
      listType = "ordered";
      listItems.push(listMatch[1]);
      return;
    }

    const bulletMatch = trimmed.match(/^[-*]\s+(.*)$/);
    if (bulletMatch) {
      if (listType && listType !== "unordered") {
        flushList();
      }
      listType = "unordered";
      listItems.push(bulletMatch[1]);
      return;
    }

    flushList();
    blocks.push(
      <p key={`p-${index}`} className="text-[15px] leading-8 text-slate-700">
        {formatInline(trimmed)}
      </p>
    );
  });

  flushList();
  return blocks;
}

export function ResultBox({ children, className = "" }) {
  const content = typeof children === "string" ? children : String(children);

  return (
    <div className={`rounded-[1.25rem] border border-white/70 bg-[linear-gradient(145deg,rgba(255,255,255,0.98),rgba(244,249,255,0.96))] p-6 shadow-[0_22px_50px_rgba(103,170,249,0.12)] ${className}`}>
      <div className="space-y-4">{renderStructuredContent(content)}</div>
    </div>
  );
}
