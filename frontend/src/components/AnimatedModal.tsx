import { useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";

export type AnimatedModalProps = {
  open: boolean;
  onClose: () => void;
  anchorRect: DOMRect | null;
  children: React.ReactNode;
};

export function AnimatedModal({ open, onClose, anchorRect, children }: AnimatedModalProps) {
  const vw = typeof window !== "undefined" ? window.innerWidth : 0;
  const vh = typeof window !== "undefined" ? window.innerHeight : 0;
  const centerX = vw / 2;
  const centerY = vh / 2;

  const { initX, initY } = anchorRect
    ? {
        initX: anchorRect.left + anchorRect.width / 2 - centerX,
        initY: anchorRect.top + anchorRect.height / 2 - centerY,
      }
    : { initX: 0, initY: 0 };

  useEffect(() => {
    if (open) document.body.style.overflow = "hidden";
    else document.body.style.overflow = "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center"
          initial={{ opacity: 1 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 1 }}
        >
          <motion.div
            className="absolute inset-0 bg-black/50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.5 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          <motion.div
            className="relative z-10 w-[min(92vw,640px)] max-h-[85vh] overflow-auto rounded-2xl bg-white dark:bg-gray-900 shadow-2xl"
            initial={{ x: initX, y: initY, scale: 0.2, opacity: 0, borderRadius: 999 }}
            animate={{ x: 0, y: 0, scale: 1, opacity: 1, borderRadius: 16 }}
            exit={{ x: initX, y: initY, scale: 0.2, opacity: 0, borderRadius: 999 }}
            transition={{ type: "spring", stiffness: 320, damping: 32, mass: 0.8 }}
          >
            {children}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
