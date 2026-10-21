import { useEffect, useId, useMemo, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Check, X, Loader2, RotateCcw, Sparkles } from 'lucide-react';
import { api } from '../../api/client';
import MarkdownBlock, { renderInline } from './MarkdownBlock';
import { timeAgo } from '../../utils/timeAgo';
import './PracticeQuestions.css';

const QUIZ_CODE_CLASS = 'concept-check__code-block';

/**
 * Accepts both API presentation items ({ presentationId, questionText, options:
 * [{ optionKey, optionText }], previousAttempt }) and the static lessonInteractions
 * shape ({ id, question, options: [{ id, label, text }], correctOptionId, explanation }).
 */
export function normalizeQuestion(item, group = 'main') {
  return {
    ...item,
    key: String(item.presentationId || item.id),
    group,
    questionText: item.questionText || item.question || '',
    options: (item.options || []).map((option) => {
      const optionKey = option.optionKey || option.id;
      return {
        key: optionKey,
        label: String(option.label || optionKey || '').toUpperCase(),
        text: option.optionText ?? option.text ?? ''
      };
    })
  };
}

function resultFromAttempt(attempt, fresh) {
  if (!attempt) return null;
  return {
    selectedOptionKey: attempt.selectedOptionKey,
    isCorrect: Boolean(attempt.isCorrect),
    correctOptionKey: attempt.correctOptionKey,
    explanation: attempt.explanation,
    answeredAt: attempt.answeredAt,
    fresh
  };
}

function buildState(questions, additionalQuestions) {
  const items = [
    ...questions.map((question) => normalizeQuestion(question, 'main')),
    ...additionalQuestions.map((question) => normalizeQuestion(question, 'additional'))
  ];
  const results = {};
  items.forEach((item) => {
    const restored = resultFromAttempt(item.previousAttempt, false);
    if (restored) results[item.key] = restored;
  });
  return { items, results };
}

function signatureOf(list) {
  return list.map((item) => item.presentationId || item.id).join('|');
}

function PracticeQuestionItem({ item, index, result, pending, error, onSelect, onRetry }) {
  const groupId = useId();
  const questionId = `${groupId}-question`;
  const isAnswered = Boolean(result);
  const correctOption = isAnswered ? item.options.find((option) => option.key === result.correctOptionKey) : null;

  return (
    <article className="concept-check practice-question" aria-labelledby={questionId}>
      <div className="practice-question__topline">
        <p className="learning-eyebrow">QUESTION {String(index + 1).padStart(2, '0')}</p>
        {item.sourceType === 'LLM_GENERATED' && (
          <span className="practice-badge practice-badge--ai" title="This question was written with an AI assistant and reviewed for the course.">
            <Sparkles size={11} aria-hidden="true" /> AI-generated
          </span>
        )}
      </div>

      <div id={questionId} className="concept-check__question">
        <MarkdownBlock text={item.questionText} codeBlockClassName={QUIZ_CODE_CLASS} />
      </div>

      <fieldset className="concept-check__fieldset" aria-labelledby={questionId}>
        <div className="concept-check__options">
          {item.options.map((option) => {
            const optionId = `${groupId}-${option.key}`;
            const isSelected = result?.selectedOptionKey === option.key || pending?.optionKey === option.key;
            const isOptionCorrect = isAnswered && option.key === result.correctOptionKey;
            const isOptionIncorrect = isAnswered && isSelected && !result.isCorrect;

            return (
              <label
                key={option.key}
                htmlFor={optionId}
                className={`concept-check__option${isSelected ? ' is-selected' : ''}${isOptionCorrect ? ' is-correct' : ''}${isOptionIncorrect ? ' is-incorrect' : ''}`}
              >
                <input
                  id={optionId}
                  type="radio"
                  name={groupId}
                  value={option.key}
                  checked={isSelected}
                  disabled={isAnswered || Boolean(pending)}
                  onChange={() => onSelect(item, option.key)}
                />
                <span className="concept-check__radio" aria-hidden="true" />
                <span className="concept-check__option-copy">
                  <span className="concept-check__option-label">{option.label}.</span>
                  <span>{renderInline(option.text, optionId)}</span>
                </span>
                {isOptionCorrect && <Check size={14} className="practice-question__mark practice-question__mark--correct" aria-label="Correct answer" />}
                {isOptionIncorrect && <X size={14} className="practice-question__mark practice-question__mark--incorrect" aria-label="Your answer" />}
              </label>
            );
          })}
        </div>
      </fieldset>

      <div role="status" aria-live="polite" className="practice-question__live">
        {pending?.type === 'answer' && (
          <div className="concept-check__feedback">
            <div className="concept-check__feedback-heading">
              <Loader2 size={15} className="animate-spin" /> Checking answer...
            </div>
          </div>
        )}
        {pending?.type === 'retry' && (
          <div className="concept-check__feedback">
            <div className="concept-check__feedback-heading">
              <Loader2 size={15} className="animate-spin" /> Preparing a fresh attempt...
            </div>
          </div>
        )}

        {isAnswered && !pending && (
          <div className={`concept-check__feedback ${result.isCorrect ? 'concept-check__feedback--correct' : 'concept-check__feedback--incorrect'}`}>
            <div className="concept-check__feedback-heading">
              {result.isCorrect ? <Check size={15} /> : <X size={15} />}
              {result.isCorrect
                ? 'Correct.'
                : `Not quite.${correctOption ? ` The answer is ${correctOption.label}.` : ''}`}
              {!result.fresh && result.answeredAt && (
                <span className="practice-question__answered-at">Answered {timeAgo(result.answeredAt)}</span>
              )}
            </div>

            {result.explanation && (
              <details className="practice-question__explanation" open={result.fresh}>
                <summary>
                  <span className="practice-question__summary-closed">Show explanation</span>
                  <span className="practice-question__summary-open">Hide explanation</span>
                </summary>
                <MarkdownBlock
                  text={result.explanation}
                  className="practice-question__explanation-body"
                  codeBlockClassName={QUIZ_CODE_CLASS}
                />
              </details>
            )}

            <div className="concept-check__feedback-actions">
              <button type="button" className="learning-button learning-button--quiet" onClick={() => onRetry(item)}>
                <RotateCcw size={13} /> Try again
              </button>
            </div>
          </div>
        )}
      </div>

      {error && <p className="practice-question__error" role="alert">{error}</p>}
    </article>
  );
}

export default function PracticeQuestions({
  questions = [],
  additionalQuestions = [],
  title = 'Practice',
  eyebrow = 'PRACTICE',
  additionalTitle = 'Additional practice',
  id,
  isAuthenticated = false
}) {
  const headingId = useId();
  const location = useLocation();
  const signature = `${signatureOf(questions)}#${signatureOf(additionalQuestions)}`;
  const [state, setState] = useState(() => buildState(questions, additionalQuestions));
  const [pending, setPending] = useState({});
  const [errors, setErrors] = useState({});

  // Reset when the parent hands over a different question set (new chapter, sign-in).
  useEffect(() => {
    setState(buildState(questions, additionalQuestions));
    setPending({});
    setErrors({});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [signature]);

  const { items, results } = state;

  const score = useMemo(() => {
    const answered = items.filter((item) => results[item.key]);
    const correct = answered.filter((item) => results[item.key].isCorrect).length;
    return {
      total: items.length,
      correct,
      incorrect: answered.length - correct,
      unanswered: items.length - answered.length
    };
  }, [items, results]);

  const setItemPending = (key, value) => setPending((current) => {
    const next = { ...current };
    if (value) next[key] = value;
    else delete next[key];
    return next;
  });

  const setItemError = (key, message) => setErrors((current) => {
    const next = { ...current };
    if (message) next[key] = message;
    else delete next[key];
    return next;
  });

  const handleSelect = async (item, optionKey) => {
    if (results[item.key] || pending[item.key]) return;
    setItemError(item.key, null);

    if (!item.presentationId) {
      // Static (non-API) question: evaluate locally.
      setState((current) => ({
        ...current,
        results: {
          ...current.results,
          [item.key]: {
            selectedOptionKey: optionKey,
            isCorrect: optionKey === item.correctOptionId,
            correctOptionKey: item.correctOptionId,
            explanation: item.explanation,
            answeredAt: new Date().toISOString(),
            fresh: true
          }
        }
      }));
      return;
    }

    setItemPending(item.key, { type: 'answer', optionKey });
    try {
      const response = await api.v2.submitPracticeAttempt(item.presentationId, optionKey);
      setState((current) => ({
        ...current,
        results: {
          ...current.results,
          [item.key]: resultFromAttempt({ ...response, selectedOptionKey: response.selectedOptionKey || optionKey }, true)
        }
      }));
    } catch (err) {
      setItemError(item.key, err?.status === 403
        ? 'This question belongs to another account. Reload the chapter to get your own copy.'
        : 'Your answer could not be recorded. Please choose again.');
    } finally {
      setItemPending(item.key, null);
    }
  };

  const retryItem = async (item) => {
    setItemError(item.key, null);

    if (!item.presentationId) {
      setState((current) => {
        const nextResults = { ...current.results };
        delete nextResults[item.key];
        return { ...current, results: nextResults };
      });
      return;
    }

    setItemPending(item.key, { type: 'retry' });
    try {
      const freshItem = normalizeQuestion(await api.v2.retryPracticeQuestion(item.presentationId), item.group);
      setState((current) => {
        const nextResults = { ...current.results };
        delete nextResults[item.key];
        const restored = resultFromAttempt(freshItem.previousAttempt, false);
        if (restored) nextResults[freshItem.key] = restored;
        return {
          items: current.items.map((existing) => (existing.key === item.key ? freshItem : existing)),
          results: nextResults
        };
      });
    } catch {
      setItemError(item.key, 'A fresh attempt could not be prepared. Please try again.');
    } finally {
      setItemPending(item.key, null);
    }
  };

  const retryIncorrect = async () => {
    const incorrectItems = items.filter((item) => results[item.key] && !results[item.key].isCorrect && !pending[item.key]);
    await Promise.all(incorrectItems.map((item) => retryItem(item)));
  };

  if (items.length === 0) return null;

  const mainItems = items.filter((item) => item.group === 'main');
  const extraItems = items.filter((item) => item.group === 'additional');
  const renderItem = (item, index) => (
    <PracticeQuestionItem
      key={item.key}
      item={item}
      index={index}
      result={results[item.key]}
      pending={pending[item.key]}
      error={errors[item.key]}
      onSelect={handleSelect}
      onRetry={retryItem}
    />
  );

  return (
    <section className="practice-quiz" id={id} aria-labelledby={headingId}>
      <header className="practice-quiz__header">
        <div>
          <p className="learning-eyebrow">{eyebrow}</p>
          <h3 id={headingId} className="practice-quiz__title">{title}</h3>
        </div>
        <div className="practice-quiz__score">
          <span className="practice-quiz__score-text" aria-live="polite">
            {score.correct} / {score.total} correct
            {score.unanswered > 0 && ` · ${score.unanswered} unanswered`}
          </span>
          {score.incorrect > 0 && (
            <button type="button" className="learning-button" onClick={retryIncorrect}>
              <RotateCcw size={13} /> Retry incorrect ({score.incorrect})
            </button>
          )}
        </div>
      </header>

      {!isAuthenticated && (
        <p className="practice-quiz__hint">
          You can answer without an account, but answers are not saved.{' '}
          <Link to="/login" state={{ from: location }} className="learning-inline-link">Sign in to keep your answers</Link>
        </p>
      )}

      {mainItems.length > 0 && (
        <div className="practice-questions-list">
          {mainItems.map((item, index) => renderItem(item, index))}
        </div>
      )}

      {extraItems.length > 0 && (
        <>
          <h4 className="chamber-subheading practice-quiz__subheading">{additionalTitle}</h4>
          <div className="practice-questions-list">
            {extraItems.map((item, index) => renderItem(item, mainItems.length + index))}
          </div>
        </>
      )}
    </section>
  );
}
