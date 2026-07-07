import { motion } from "framer-motion";

export function SectionShell({ title, kicker, children }) {
  return (
    <motion.section
      key={title}
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.22 }}
      className="mx-auto w-full max-w-6xl"
    >
      <div className="mb-6">
        <p className="text-sm font-bold uppercase tracking-[0.18em] text-blush">{kicker}</p>
        <h2 className="mt-2 text-3xl font-black text-ink">{title}</h2>
      </div>
      {children}
    </motion.section>
  );
}
