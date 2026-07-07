import { motion } from "framer-motion";

export function Button({ children, className = "", disabled, ...props }) {
  return (
    <motion.button
      type="button"
      whileHover={!disabled ? { scale: 1.02, y: -1 } : undefined}
      whileTap={!disabled ? { scale: 0.985 } : undefined}
      disabled={disabled}
      className={`inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blush via-[#c76d95] to-[#d884a9] px-5 py-3 text-sm font-bold text-white shadow-[0_14px_28px_rgba(185,95,137,0.28)] transition disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
      {...props}
    >
      {children}
    </motion.button>
  );
}
