'use client';

import { useState } from 'react';
import { Star, X } from 'lucide-react';
import { clsx } from 'clsx';

interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { worked: boolean; rating: number; comment?: string }) => void;
  contentTitle: string;
}

export default function FeedbackModal({
  isOpen,
  onClose,
  onSubmit,
  contentTitle,
}: FeedbackModalProps) {
  const [worked, setWorked] = useState<boolean | null>(null);
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState('');
  const [hoveredRating, setHoveredRating] = useState(0);

  if (!isOpen) return null;

  const handleSubmit = () => {
    if (worked === null || rating === 0) return;
    onSubmit({ worked, rating, comment: comment || undefined });
    // Reset form
    setWorked(null);
    setRating(0);
    setComment('');
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-end sm:items-center justify-center">
      <div className="bg-white w-full max-w-lg rounded-t-2xl sm:rounded-2xl p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Give Feedback</h2>
          <button onClick={onClose} className="p-1 text-gray-400 hover:text-gray-600">
            <X className="w-6 h-6" />
          </button>
        </div>

        <p className="text-sm text-gray-600 mb-6">
          How was <span className="font-medium">&quot;{contentTitle}&quot;</span>?
        </p>

        {/* Did it work? */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Did this help solve your problem?
          </label>
          <div className="flex gap-3">
            <button
              onClick={() => setWorked(true)}
              className={clsx(
                'flex-1 py-3 rounded-lg border-2 font-medium transition-colors',
                worked === true
                  ? 'border-green-500 bg-green-50 text-green-700'
                  : 'border-gray-200 hover:border-gray-300'
              )}
            >
              Yes, it helped!
            </button>
            <button
              onClick={() => setWorked(false)}
              className={clsx(
                'flex-1 py-3 rounded-lg border-2 font-medium transition-colors',
                worked === false
                  ? 'border-red-500 bg-red-50 text-red-700'
                  : 'border-gray-200 hover:border-gray-300'
              )}
            >
              Not really
            </button>
          </div>
        </div>

        {/* Star rating */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Rate this content
          </label>
          <div className="flex gap-2 justify-center">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                onClick={() => setRating(star)}
                onMouseEnter={() => setHoveredRating(star)}
                onMouseLeave={() => setHoveredRating(0)}
                className="p-1"
              >
                <Star
                  className={clsx(
                    'w-8 h-8 transition-colors',
                    (hoveredRating || rating) >= star
                      ? 'text-yellow-400 fill-current'
                      : 'text-gray-300'
                  )}
                />
              </button>
            ))}
          </div>
        </div>

        {/* Comment */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Additional comments (optional)
          </label>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Share your thoughts..."
            className="input-field h-24 resize-none"
          />
        </div>

        {/* Submit */}
        <button
          onClick={handleSubmit}
          disabled={worked === null || rating === 0}
          className="btn-primary w-full"
        >
          Submit Feedback
        </button>
      </div>
    </div>
  );
}
