'use client';

import { Mic, MicOff, Loader2 } from 'lucide-react';
import { clsx } from 'clsx';

interface VoiceButtonProps {
  isRecording: boolean;
  isProcessing?: boolean;
  onStart: () => void;
  onStop: () => void;
  disabled?: boolean;
}

export default function VoiceButton({
  isRecording,
  isProcessing = false,
  onStart,
  onStop,
  disabled = false,
}: VoiceButtonProps) {
  const handleClick = () => {
    if (isRecording) {
      onStop();
    } else {
      onStart();
    }
  };

  return (
    <div className="relative inline-flex items-center justify-center">
      {/* Pulse animation when recording */}
      {isRecording && (
        <div className="absolute inset-0 rounded-full bg-red-400 recording-pulse" />
      )}
      
      <button
        onClick={handleClick}
        disabled={disabled || isProcessing}
        className={clsx(
          'relative w-16 h-16 rounded-full flex items-center justify-center',
          'transition-all duration-200 shadow-lg',
          isRecording
            ? 'bg-red-500 hover:bg-red-600 text-white'
            : 'bg-primary-600 hover:bg-primary-700 text-white',
          (disabled || isProcessing) && 'opacity-50 cursor-not-allowed'
        )}
      >
        {isProcessing ? (
          <Loader2 className="w-8 h-8 animate-spin" />
        ) : isRecording ? (
          <MicOff className="w-8 h-8" />
        ) : (
          <Mic className="w-8 h-8" />
        )}
      </button>
      
      <span className="absolute -bottom-6 text-sm text-gray-600 whitespace-nowrap">
        {isProcessing ? 'Processing...' : isRecording ? 'Tap to stop' : 'Tap to speak'}
      </span>
    </div>
  );
}
