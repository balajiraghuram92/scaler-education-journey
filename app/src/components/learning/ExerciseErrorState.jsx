import { AlertCircle, RefreshCw } from 'lucide-react';

function getErrorCopy(error) {
  if (error?.status === 429) {
    return {
      title: 'The exercise runner is busy',
      message: 'Please wait a moment and try again.'
    };
  }

  if (error?.status === 404) {
    return {
      title: 'Exercise unavailable',
      message: 'This exercise is not available for the current lesson.'
    };
  }

  if (error?.status === 400 || error?.status === 422) {
    return {
      title: 'Submission could not be sent',
      message: 'Review the editable files and try again.'
    };
  }

  return {
    title: 'Neuralascent could not execute your code',
    message: 'The exercise service is temporarily unavailable. Please try again shortly.'
  };
}

export default function ExerciseErrorState({ error, onRetry }) {
  const copy = getErrorCopy(error);

  return (
    <div className="exercise-error-state" role="alert">
      <AlertCircle size={17} aria-hidden="true" />
      <div>
        <h4>{copy.title}</h4>
        <p>{copy.message}</p>
      </div>
      {onRetry && (
        <button type="button" className="learning-button learning-button--quiet" onClick={onRetry}>
          <RefreshCw size={13} /> Try again
        </button>
      )}
    </div>
  );
}
