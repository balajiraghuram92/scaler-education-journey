import { useId, useState } from 'react';
import { Check, X } from 'lucide-react';
import { formatInline } from './formatUtils';

function PracticeQuestionItem({ item, index }) {
  const groupId = useId();
  const [selectedOption, setSelectedOption] = useState(null);

  const isSubmitted = selectedOption !== null;
  const isCorrect = isSubmitted && selectedOption === item.correctOptionId;

  return (
    <article className="concept-check" aria-labelledby={`${groupId}-title`}>
      <p className="learning-eyebrow">QUESTION {String(index + 1).padStart(2, '0')}</p>
      <fieldset className="concept-check__fieldset">
        <legend id={`${groupId}-title`} className="concept-check__question">
          {formatInline(item.question)}
        </legend>

        {item.codeBlock && (
          <pre className="concept-check__code-block"><code>{item.codeBlock}</code></pre>
        )}

        <div className="concept-check__options">
          {item.options.map((option) => {
            const optionId = `${groupId}-${option.id}`;
            const isSelected = selectedOption === option.id;
            const isOptionCorrect = isSubmitted && option.id === item.correctOptionId;
            const isOptionIncorrect = isSubmitted && isSelected && option.id !== item.correctOptionId;

            return (
              <label
                key={option.id}
                htmlFor={optionId}
                className={`concept-check__option${isSelected ? ' is-selected' : ''}${isOptionCorrect ? ' is-correct' : ''}${isOptionIncorrect ? ' is-incorrect' : ''}`}
              >
                <input
                  id={optionId}
                  type="radio"
                  name={groupId}
                  value={option.id}
                  checked={isSelected}
                  disabled={isSubmitted}
                  onChange={() => setSelectedOption(option.id)}
                />
                <span className="concept-check__radio" aria-hidden="true" />
                <span className="concept-check__option-copy">
                  <span className="concept-check__option-label">{option.label}.</span>
                  <span>{formatInline(option.text)}</span>
                </span>
              </label>
            );
          })}
        </div>
      </fieldset>

      {isSubmitted && (
        <div
          className={`concept-check__feedback ${isCorrect ? 'concept-check__feedback--correct' : 'concept-check__feedback--incorrect'}`}
          role="status"
          aria-live="polite"
        >
          <div className="concept-check__feedback-heading">
            {isCorrect ? <Check size={15} /> : <X size={15} />} {isCorrect ? 'Correct.' : 'Not quite.'}
          </div>
          <p>{formatInline(item.explanation)}</p>
        </div>
      )}
    </article>
  );
}

export default function PracticeQuestions({ questions = [] }) {
  if (!questions || questions.length === 0) return null;

  return (
    <section className="practice-questions-section" aria-label="Practice Questions">
      <div className="practice-questions-header" style={{ margin: '2rem 0 1rem' }}>
        <p className="learning-eyebrow">PRACTICE — {questions.length} QUESTIONS</p>
      </div>
      <div className="practice-questions-list">
        {questions.map((q, idx) => (
          <PracticeQuestionItem key={q.id || idx} item={q} index={idx} />
        ))}
      </div>
    </section>
  );
}
