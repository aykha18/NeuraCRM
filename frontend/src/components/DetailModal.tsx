import { Dialog } from "@headlessui/react";
import { X } from "lucide-react";
import React from "react";

interface DetailModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

const DetailModal: React.FC<DetailModalProps> = ({ open, onClose, title, children }) => (
  <Dialog open={open} onClose={onClose} className="fixed z-50 inset-0 overflow-y-auto">
    <div className="flex items-center justify-center min-h-screen px-4">
      <div className="fixed inset-0 bg-black bg-opacity-30" aria-hidden="true" />
      <div className="relative bg-white dark:bg-gray-900 rounded-2xl p-8 max-w-md w-full mx-auto z-10 shadow-xl border border-gray-200 dark:border-gray-800">
        <button
          className="absolute top-4 right-4 p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800"
          onClick={onClose}
          title="Close"
        >
          <X className="w-5 h-5 text-gray-500" />
        </button>
        <Dialog.Title className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">{title}</Dialog.Title>
        <div className="space-y-2 text-lg">{children}</div>
      </div>
    </div>
  </Dialog>
);

export default DetailModal; 