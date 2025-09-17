import { Dialog, Transition } from "@headlessui/react";
import { X } from "lucide-react";
import React, { Fragment } from "react";

interface AnimatedModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  animationType?: 'slideUp' | 'scale' | 'fade' | 'slideDown';
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

const AnimatedModal: React.FC<AnimatedModalProps> = ({ 
  open, 
  onClose, 
  title, 
  children, 
  animationType = 'scale',
  size = 'md'
}) => {
  const sizeClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl'
  };

  const getAnimationClasses = () => {
    switch (animationType) {
      case 'slideUp':
        return {
          enter: 'transform transition-all duration-300 ease-out',
          enterFrom: 'translate-y-full opacity-0',
          enterTo: 'translate-y-0 opacity-100',
          leave: 'transform transition-all duration-200 ease-in',
          leaveFrom: 'translate-y-0 opacity-100',
          leaveTo: 'translate-y-full opacity-0'
        };
      case 'scale':
        return {
          enter: 'transform transition-all duration-300 ease-out',
          enterFrom: 'scale-95 opacity-0',
          enterTo: 'scale-100 opacity-100',
          leave: 'transform transition-all duration-200 ease-in',
          leaveFrom: 'scale-100 opacity-100',
          leaveTo: 'scale-95 opacity-0'
        };
      case 'fade':
        return {
          enter: 'transition-opacity duration-300 ease-out',
          enterFrom: 'opacity-0',
          enterTo: 'opacity-100',
          leave: 'transition-opacity duration-200 ease-in',
          leaveFrom: 'opacity-100',
          leaveTo: 'opacity-0'
        };
      case 'slideDown':
        return {
          enter: 'transform transition-all duration-300 ease-out',
          enterFrom: '-translate-y-full opacity-0',
          enterTo: 'translate-y-0 opacity-100',
          leave: 'transform transition-all duration-200 ease-in',
          leaveFrom: 'translate-y-0 opacity-100',
          leaveTo: '-translate-y-full opacity-0'
        };
      default:
        return {
          enter: 'transform transition-all duration-300 ease-out',
          enterFrom: 'scale-95 opacity-0',
          enterTo: 'scale-100 opacity-100',
          leave: 'transform transition-all duration-200 ease-in',
          leaveFrom: 'scale-100 opacity-100',
          leaveTo: 'scale-95 opacity-0'
        };
    }
  };

  const animationClasses = getAnimationClasses();

  return (
    <Transition appear show={open} as={Fragment}>
      <Dialog as="div" className="fixed z-50 inset-0 overflow-y-auto" onClose={onClose}>
        <div className="flex items-center justify-center min-h-screen px-4">
          {/* Backdrop */}
          <Transition.Child
            as={Fragment}
            enter="transition-opacity duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="transition-opacity duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm" />
          </Transition.Child>

          {/* Modal Panel */}
          <Transition.Child
            as={Fragment}
            enter={animationClasses.enter}
            enterFrom={animationClasses.enterFrom}
            enterTo={animationClasses.enterTo}
            leave={animationClasses.leave}
            leaveFrom={animationClasses.leaveFrom}
            leaveTo={animationClasses.leaveTo}
          >
            <div className={`relative bg-white dark:bg-gray-900 rounded-2xl p-8 ${sizeClasses[size]} w-full mx-auto z-10 shadow-2xl border border-gray-200 dark:border-gray-800`}>
              {/* Close Button */}
              <button
                className="absolute top-4 right-4 p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-200 group"
                onClick={onClose}
                title="Close"
              >
                <X className="w-5 h-5 text-gray-500 group-hover:text-gray-700 dark:group-hover:text-gray-300 transition-colors duration-200" />
              </button>
              
              {/* Title */}
              <Dialog.Title className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">
                {title}
              </Dialog.Title>
              
              {/* Content */}
              <div className="space-y-2 text-lg">
                {children}
              </div>
            </div>
          </Transition.Child>
        </div>
      </Dialog>
    </Transition>
  );
};

export default AnimatedModal;