import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';

export default function VerticalDetail() {
  const { id } = useParams();
  const [vertical, setVertical] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/verticals')
      .then(res => res.json())
      .then(data => {
        const found = data.find(v => v.id === parseInt(id));
        setVertical(found);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to fetch vertical:', err);
        setLoading(false);
      });
  }, [id]);

  const toggleTask = async (taskId) => {
    try {
      const response = await fetch(`/api/tasks/${taskId}/toggle`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
      });
      const updatedTask = await response.json();
      
      setVertical(prev => {
        if (!prev) return null;
        return {
          ...prev,
          tasks: prev.tasks.map(t => 
            t.id === taskId ? { ...t, isCompleted: updatedTask.isCompleted } : t
          ),
        };
      });
    } catch (err) {
      console.error('Failed to toggle task:', err);
    }
  };

  // Calculate progress
  const totalTasks = vertical?.tasks.length || 0;
  const completedTasks = vertical?.tasks.filter(t => t.isCompleted).length || 0;
  const progress = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;

  if (loading) return <p className="text-secondary">Loading...</p>;
  if (!vertical) return <p className="text-secondary">Vertical not found</p>;

  return (
    <div className="mt-md">
      {/* Vertical Header */}
      <div className="glass-panel vertical-detail__header">
        <h1 className="gradient-text mb-md vertical-detail__title">
          {vertical.name}
        </h1>
        <p className="text-secondary vertical-detail__description">
          {vertical.description}
        </p>
        
        {/* Master Progress Bar */}
        {totalTasks > 0 && (
          <div className="vertical-detail__master-progress">
            <div className="vertical-detail__master-progress-header">
              <span className="vertical-detail__master-progress-label">Total Progress</span>
              <span className="vertical-detail__master-progress-value">
                {Math.round(progress)}% ({completedTasks}/{totalTasks})
              </span>
            </div>
            <div className="vertical-detail__master-progress-track">
              <div
                className="vertical-detail__master-progress-fill"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}
        
        <Link to="/" className="btn btn-secondary vertical-detail__back-btn">
          ← Back to Verticals
        </Link>
      </div>

      {/* Tasks List */}
      <section className="mt-xl vertical-detail__tasks-section">
        <h2 className="mb-lg vertical-detail__tasks-title">
          Tasks <span className="text-secondary">({completedTasks}/{totalTasks} completed)</span>
        </h2>
        <div className="vertical-detail__tasks-list">
          {vertical.tasks.length === 0 ? (
            <p className="text-secondary">No tasks yet</p>
          ) : (
            vertical.tasks.map(task => (
              <div
                key={task.id}
                className={`glass-panel vertical-task ${task.isCompleted ? 'vertical-task--completed' : ''}`}
                onClick={() => toggleTask(task.id)}
              >
                <div className="vertical-task__checkmark">
                  {task.isCompleted ? (
                    <svg
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="white"
                      strokeWidth="3"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  ) : null}
                </div>
                <span className="vertical-task__title">{task.title}</span>
                {task.isCompleted && (
                  <span className="vertical-task__badge">✓ Done</span>
                )}
              </div>
            ))
          )}
        </div>
      </section>
    </div>
  );
}
