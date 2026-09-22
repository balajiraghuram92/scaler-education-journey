import { useEffect, useId, useState } from 'react';
import { Check, X, Loader2 } from 'lucide-react';
import { api } from '../../api/client';
import { formatInline } from './formatUtils';

function PracticeQuestionItem({ item, index }) {
  const groupId = useId();
  const [selectedOption, setSelectedOption] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [submissionResult, setSubmissionResult] = useState(null);

  const isSubmitted = submissionResult !== null;
  const isCorrect = submissionResult?.isCorrect ?? false;

  const handleSelectOption = async (optionKey) => {
    if (selectedOption !== null || submitting) return;
    setSelectedOption(optionKey);

    // If dynamic presentation from server
    if (item.presentationId) {
      setSubmitting(true);
      try {
        const res = await api.v2.submitPracticeAttempt(item.presentationId, optionKey);
        setSubmissionResult({
          isCorrect: res.isCorrect,
          correctOptionKey: res.correctOptionKey,
          explanation: res.explanation
        });
      } catch (err) {
        console.error('Error submitting practice attempt:', err);
        // Fallback to client-side evaluation if available
        const isClientCorrect = item.correctOptionId ? optionKey === item.correctOptionId : false;
        setSubmissionResult({
          isCorrect: isClientCorrect,
          correctOptionKey: item.correctOptionId || optionKey,
          explanation: item.explanation || 'Answer recorded.'
        });
      } finally {
        setSubmitting(false);
      }
    } else {
      // Static fallback mode
      const clientCorrect = optionKey === item.correctOptionId;
      setSubmissionResult({
        isCorrect: clientCorrect,
        correctOptionKey: item.correctOptionId,
        explanation: item.explanation
      });
    }
  };

  const questionText = item.questionText || item.question || '';
  const options = item.options || [];

  return (
    <article className="concept-check" aria-labelledby={`${groupId}-title`}>
      <p className="learning-eyebrow">QUESTION {String(index + 1).padStart(2, '0')}</p>
      <fieldset className="concept-check__fieldset">
        <legend id={`${groupId}-title`} className="concept-check__question">
          {formatInline(questionText)}
        </legend>

        {item.codeBlock && (
          <pre className="concept-check__code-block"><code>{item.codeBlock}</code></pre>
        )}

        <div className="concept-check__options">
          {options.map((option) => {
            const optKey = option.optionKey || option.id;
            const optLabel = option.label || optKey?.toUpperCase();
            const optText = option.optionText || option.text || '';
            const optionId = `${groupId}-${optKey}`;
            const isSelected = selectedOption === optKey;
            const isOptionCorrect = isSubmitted && optKey === submissionResult.correctOptionKey;
            const isOptionIncorrect = isSubmitted && isSelected && !submissionResult.isCorrect;

            return (
              <label
                key={optKey}
                htmlFor={optionId}
                className={`concept-check__option${isSelected ? ' is-selected' : ''}${isOptionCorrect ? ' is-correct' : ''}${isOptionIncorrect ? ' is-incorrect' : ''}`}
              >
                <input
                  id={optionId}
                  type="radio"
                  name={groupId}
                  value={optKey}
                  checked={isSelected}
                  disabled={isSubmitted || submitting}
                  onChange={() => handleSelectOption(optKey)}
                />
                <span className="concept-check__radio" aria-hidden="true" />
                <span className="concept-check__option-copy">
                  <span className="concept-check__option-label">{optLabel}.</span>
                  <span>{formatInline(optText)}</span>
                </span>
              </label>
            );
          })}
        </div>
      </fieldset>

      {submitting && (
        <div className="concept-check__feedback" role="status" aria-live="polite">
          <div className="concept-check__feedback-heading" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Loader2 size={15} className="animate-spin" /> Evaluating answer...
          </div>
        </div>
      )}

      {isSubmitted && (
        <div
          className={`concept-check__feedback ${isCorrect ? 'concept-check__feedback--correct' : 'concept-check__feedback--incorrect'}`}
          role="status"
          aria-live="polite"
        >
          <div className="concept-check__feedback-heading">
            {isCorrect ? <Check size={15} /> : <X size={15} />} {isCorrect ? 'Correct.' : 'Not quite.'}
          </div>
          {submissionResult.explanation && (
            <p>{formatInline(submissionResult.explanation)}</p>
          )}
        </div>
      )}
    </article>
  );
}

export default function PracticeQuestions({
  courseSlug,
  moduleSlug,
  lessonSlug,
  questions: staticQuestions = []
}) {
  const [questions, setQuestions] = useState(staticQuestions);
  const [loading, setLoading] = useState(Boolean(courseSlug && moduleSlug && lessonSlug));

  useEffect(() => {
    let isMounted = true;

    async function fetchQuestions() {
      if (!courseSlug || !moduleSlug || !lessonSlug) {
        setQuestions(staticQuestions);
        setLoading(false);
        return;
      }

      setLoading(true);
      try {
        const dynamicQuestions = await api.v2.getPracticeQuestions(courseSlug, moduleSlug, lessonSlug);
        if (isMounted) {
          if (Array.isArray(dynamicQuestions) && dynamicQuestions.length > 0) {
            setQuestions(dynamicQuestions);
          } else {
            setQuestions(staticQuestions);
          }
        }
      } catch (err) {
        console.warn('Could not fetch dynamic practice questions; falling back to static:', err);
        if (isMounted) {
          setQuestions(staticQuestions);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    fetchQuestions();

    return () => {
      isMounted = false;
    };
  }, [courseSlug, moduleSlug, lessonSlug]);

  if (loading && (!questions || questions.length === 0)) {
    return (
      <section className="practice-questions-section" aria-label="Practice Questions">
        <div className="practice-questions-header" style={{ margin: '2rem 0 1rem' }}>
          <p className="learning-eyebrow">PRACTICE — LOADING QUESTIONS...</p>
        </div>
      </section>
    );
  }

  if (!questions || questions.length === 0) return null;

  return (
    <section className="practice-questions-section" aria-label="Practice Questions">
      <div className="practice-questions-header" style={{ margin: '2rem 0 1rem' }}>
        <p className="learning-eyebrow">PRACTICE — {questions.length} QUESTIONS</p>
      </div>
      <div className="practice-questions-list">
        {questions.map((q, idx) => (
          <PracticeQuestionItem key={q.presentationId || q.id || idx} item={q} index={idx} />
        ))}
      </div>
    </section>
  );
}
