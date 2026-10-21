import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import PracticeQuestions from '../../components/learning/PracticeQuestions';

const { submitPracticeAttempt, retryPracticeQuestion } = vi.hoisted(() => ({
  submitPracticeAttempt: vi.fn(),
  retryPracticeQuestion: vi.fn()
}));

vi.mock('../../api/client', () => ({
  api: { v2: { submitPracticeAttempt, retryPracticeQuestion } }
}));

const options = [
  { optionKey: 'a', optionText: 'It returns the same instance' },
  { optionKey: 'b', optionText: 'It creates a new instance each call' }
];

function question(overrides) {
  return {
    presentationId: 'p-1',
    questionId: 1,
    category: 'Assignment',
    sourceType: 'FROM_MATERIAL',
    questionText: 'What does `Config()` return?',
    options,
    previousAttempt: null,
    attemptCount: 0,
    ...overrides
  };
}

function renderQuiz(props) {
  return render(
    <MemoryRouter>
      <PracticeQuestions title="Assignment" eyebrow="PRACTICE" {...props} />
    </MemoryRouter>
  );
}

beforeEach(() => {
  submitPracticeAttempt.mockReset();
  retryPracticeQuestion.mockReset();
});

describe('PracticeQuestions', () => {
  it('restores a previous attempt with a collapsed explanation and a score header', () => {
    const { container } = renderQuiz({
      isAuthenticated: true,
      questions: [
        question({
          presentationId: 'p-1',
          previousAttempt: {
            selectedOptionKey: 'b',
            isCorrect: false,
            correctOptionKey: 'a',
            explanation: 'Because `__new__` caches **the instance**.',
            answeredAt: new Date(Date.now() - 3 * 3600 * 1000).toISOString()
          }
        }),
        question({ presentationId: 'p-2', questionText: 'Second question' })
      ]
    });

    expect(screen.getByText('0 / 2 correct · 1 unanswered')).toBeInTheDocument();

    const [first] = screen.getAllByRole('article');
    const selected = within(first).getByRole('radio', { name: /new instance/ });
    expect(selected).toBeChecked();
    expect(selected).toBeDisabled();
    expect(selected.closest('label')).toHaveClass('is-incorrect');
    expect(within(first).getByRole('radio', { name: /same instance/ }).closest('label')).toHaveClass('is-correct');
    expect(within(first).getByText(/Not quite\. The answer is A\./)).toBeInTheDocument();
    expect(within(first).getByText(/Answered 3 hours ago/)).toBeInTheDocument();

    const details = container.querySelector('details.practice-question__explanation');
    expect(details).not.toHaveAttribute('open');
    expect(within(details).getByText('the instance').tagName).toBe('STRONG');
    expect(screen.getByRole('button', { name: /Retry incorrect \(1\)/ })).toBeInTheDocument();
  });

  it('submits an answer and opens the explanation right away', async () => {
    submitPracticeAttempt.mockResolvedValue({
      isCorrect: true,
      correctOptionKey: 'a',
      explanation: 'Correct: the cached instance is returned.',
      selectedOptionKey: 'a',
      answeredAt: new Date().toISOString()
    });
    const { container } = renderQuiz({ isAuthenticated: true, questions: [question()] });

    fireEvent.click(screen.getByRole('radio', { name: /same instance/ }));

    await screen.findByText('Correct.');
    expect(submitPracticeAttempt).toHaveBeenCalledWith('p-1', 'a');
    expect(container.querySelector('details.practice-question__explanation')).toHaveAttribute('open');
    expect(screen.getByText('1 / 1 correct')).toBeInTheDocument();
  });

  it('replaces an answered item with a fresh presentation on Try again', async () => {
    retryPracticeQuestion.mockResolvedValue(question({ presentationId: 'p-9', questionText: 'Fresh copy of the question' }));
    renderQuiz({
      isAuthenticated: true,
      questions: [question({
        previousAttempt: { selectedOptionKey: 'b', isCorrect: false, correctOptionKey: 'a', explanation: 'x', answeredAt: null }
      })]
    });

    fireEvent.click(screen.getByRole('button', { name: /Try again/ }));

    await screen.findByText('Fresh copy of the question');
    expect(retryPracticeQuestion).toHaveBeenCalledWith('p-1');
    expect(screen.getByRole('radio', { name: /new instance/ })).not.toBeChecked();
    expect(screen.getByRole('radio', { name: /new instance/ })).toBeEnabled();
    expect(screen.getByText('0 / 1 correct · 1 unanswered')).toBeInTheDocument();
  });

  it('retries every incorrect question from the score header', async () => {
    retryPracticeQuestion.mockImplementation(async (id) => question({ presentationId: `${id}-new`, questionText: `Retry of ${id}` }));
    const wrong = { selectedOptionKey: 'b', isCorrect: false, correctOptionKey: 'a', explanation: 'x', answeredAt: null };
    const right = { selectedOptionKey: 'a', isCorrect: true, correctOptionKey: 'a', explanation: 'y', answeredAt: null };
    renderQuiz({
      isAuthenticated: true,
      questions: [
        question({ presentationId: 'p-1', previousAttempt: wrong }),
        question({ presentationId: 'p-2', previousAttempt: right })
      ],
      additionalQuestions: [question({ presentationId: 'p-3', category: 'Additional', previousAttempt: wrong })]
    });

    expect(screen.getByRole('heading', { name: 'Additional practice' })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /Retry incorrect \(2\)/ }));

    await waitFor(() => expect(screen.getByText('Retry of p-3')).toBeInTheDocument());
    expect(screen.getByText('Retry of p-1')).toBeInTheDocument();
    expect(retryPracticeQuestion).toHaveBeenCalledTimes(2);
    expect(retryPracticeQuestion).not.toHaveBeenCalledWith('p-2');
    expect(screen.getByText('1 / 3 correct · 2 unanswered')).toBeInTheDocument();
  });

  it('marks AI-generated questions and tells signed-out learners answers are not saved', () => {
    renderQuiz({ isAuthenticated: false, questions: [question({ sourceType: 'LLM_GENERATED' })] });

    expect(screen.getByText('AI-generated')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Sign in to keep your answers/ })).toHaveAttribute('href', '/login');
  });

  it('renders fenced code with blank lines inside the question text', () => {
    const { container } = renderQuiz({
      questions: [question({ questionText: 'Given:\n\n```python\na = 1\n\nb = 2\n```\n\nWhat is `b`?' })]
    });

    const code = container.querySelector('.concept-check__question pre.concept-check__code-block code');
    expect(code.textContent).toBe('a = 1\n\nb = 2');
  });

  it('evaluates static (non-API) questions locally', () => {
    renderQuiz({
      questions: [{
        id: 'static-1',
        question: 'Pick B',
        options: [{ id: 'a', label: 'A', text: 'No' }, { id: 'b', label: 'B', text: 'Yes' }],
        correctOptionId: 'b',
        explanation: 'B is right.'
      }]
    });

    fireEvent.click(screen.getByRole('radio', { name: /Yes/ }));
    expect(screen.getByText('Correct.')).toBeInTheDocument();
    expect(submitPracticeAttempt).not.toHaveBeenCalled();
  });
});
