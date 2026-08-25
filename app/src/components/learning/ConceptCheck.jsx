import { useId, useState } from 'react';
import { Check, Lightbulb, RotateCcw, X } from 'lucide-react';

export default function ConceptCheck({
  eyebrow = 'CONCEPT CHECK',
  question,
  options = [],
  correctOptionId,
  explanation,
  incorrectExplanation,
  hint,
  initialSelectedOption = null,
  initialSubmitted = false
}) {
  const groupId = useId();
  const [selectedOption, setSelectedOption] = useState(initialSelectedOption);
  const [submitted, setSubmitted] = useState(initialSubmitted);
  const [showHint, setShowHint] = useState(false);

  const result = submitted
    ? selectedOption === correctOptionId ? 'correct' : 'incorrect'
    : null;

  const handleSubmit = (event) => {
    event.preventDefault();
    if (selectedOption) setSubmitted(true);
  };

  const handleRetry = () => {
    setSelectedOption(null);
    setSubmitted(false);
    setShowHint(false);
  };

  return (
    <section className="concept-check" aria-labelledby={`${groupId}-title`}>
      <form onSubmit={handleSubmit}>
        <p className="learning-eyebrow">{eyebrow}</p>
        <fieldset className="concept-check__fieldset">
          <legend id={`${groupId}-title`} className="concept-check__question">
            {question}
          </legend>

          <div className="concept-check__options">
            {options.map((option) => {
              const optionId = `${groupId}-${option.id}`;
              const isSelected = selectedOption === option.id;
              const isCorrect = submitted && option.id === correctOptionId;
              const isIncorrect = submitted && isSelected && option.id !== correctOptionId;

              return (
                <label
                  key={option.id}
                  htmlFor={optionId}
                  className={`concept-check__option${isSelected ? ' is-selected' : ''}${isCorrect ? ' is-correct' : ''}${isIncorrect ? ' is-incorrect' : ''}`}
                >
                  <input
                    id={optionId}
                    type="radio"
                    name={groupId}
                    value={option.id}
                    checked={isSelected}
                    disabled={submitted}
                    onChange={() => setSelectedOption(option.id)}
                  />
                  <span className="concept-check__radio" aria-hidden="true" />
                  <span className="concept-check__option-copy">
                    <span className="concept-check__option-label">{option.label}.</span>
                    <span>{option.text}</span>
                  </span>
                </label>
              );
            })}
          </div>
        </fieldset>

        {!submitted && (
          <button type="submit" className="learning-button learning-button--quiet" disabled={!selectedOption}>
            Check answer
          </button>
        )}

        {result === 'correct' && (
          <div className="concept-check__feedback concept-check__feedback--correct" role="status" aria-live="polite">
            <div className="concept-check__feedback-heading"><Check size={15} /> Correct.</div>
            <p>{explanation}</p>
            <a className="learning-inline-link" href="#practical-backend-scenario">
              Continue reading <span aria-hidden="true">→</span>
            </a>
          </div>
        )}

        {result === 'incorrect' && (
          <div className="concept-check__feedback concept-check__feedback--incorrect" role="status" aria-live="polite">
            <div className="concept-check__feedback-heading"><X size={15} /> Not quite.</div>
            <p>{incorrectExplanation}</p>
            <div className="concept-check__feedback-actions">
              <button type="button" className="learning-button learning-button--quiet" onClick={handleRetry}>
                <RotateCcw size={13} /> Try again
              </button>
              <button type="button" className="learning-text-button" onClick={() => setShowHint((current) => !current)}>
                <Lightbulb size={13} /> {showHint ? 'Hide hint' : 'Hint'}
              </button>
            </div>
            {showHint && <p className="concept-check__hint">{hint}</p>}
          </div>
        )}
      </form>
    </section>
  );
}
