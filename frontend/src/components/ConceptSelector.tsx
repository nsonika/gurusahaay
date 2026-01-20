'use client';

import { useState, useEffect } from 'react';
import { Concept, getConcepts } from '@/lib/api';
import { ChevronDown, Check } from 'lucide-react';
import { clsx } from 'clsx';

interface ConceptSelectorProps {
  value: string;
  onChange: (conceptId: string) => void;
  language?: string;
  placeholder?: string;
}

export default function ConceptSelector({
  value,
  onChange,
  language,
  placeholder = 'Select a topic...',
}: ConceptSelectorProps) {
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getConcepts(language)
      .then(setConcepts)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [language]);

  const selectedConcept = concepts.find((c) => c.concept_id === value);

  // Get display term in preferred language
  const getDisplayTerm = (concept: Concept) => {
    const langSynonym = concept.synonyms.find((s) => s.language === language);
    if (langSynonym) return langSynonym.term;
    const enSynonym = concept.synonyms.find((s) => s.language === 'en');
    if (enSynonym) return enSynonym.term;
    return concept.concept_id;
  };

  // Group concepts by subject
  const groupedConcepts = concepts.reduce((acc, concept) => {
    const subject = concept.subject || 'Other';
    if (!acc[subject]) acc[subject] = [];
    acc[subject].push(concept);
    return acc;
  }, {} as Record<string, Concept[]>);

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={clsx(
          'w-full px-4 py-3 text-left border rounded-lg',
          'flex items-center justify-between',
          'focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
          isOpen ? 'border-primary-500' : 'border-gray-300'
        )}
      >
        <span className={selectedConcept ? 'text-gray-900' : 'text-gray-400'}>
          {loading ? 'Loading...' : selectedConcept ? getDisplayTerm(selectedConcept) : placeholder}
        </span>
        <ChevronDown className={clsx('w-5 h-5 text-gray-400 transition-transform', isOpen && 'rotate-180')} />
      </button>

      {isOpen && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-64 overflow-y-auto">
          {Object.entries(groupedConcepts).map(([subject, subjectConcepts]) => (
            <div key={subject}>
              <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase bg-gray-50">
                {subject}
              </div>
              {subjectConcepts.map((concept) => (
                <button
                  key={concept.concept_id}
                  type="button"
                  onClick={() => {
                    onChange(concept.concept_id);
                    setIsOpen(false);
                  }}
                  className={clsx(
                    'w-full px-4 py-3 text-left flex items-center justify-between',
                    'hover:bg-gray-50',
                    value === concept.concept_id && 'bg-primary-50'
                  )}
                >
                  <div>
                    <div className="font-medium text-gray-900">{getDisplayTerm(concept)}</div>
                    {concept.description_en && (
                      <div className="text-sm text-gray-500">{concept.description_en}</div>
                    )}
                  </div>
                  {value === concept.concept_id && (
                    <Check className="w-5 h-5 text-primary-600" />
                  )}
                </button>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
