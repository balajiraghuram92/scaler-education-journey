import { useState, useEffect, useCallback } from 'react';
import { api, ApiError } from '../api/client';
import { useAuth } from '../context/AuthContext';
import {
  Users,
  Check,
  X,
  Clock,
  AlertTriangle,
  RefreshCw,
  Mail,
  Calendar,
  UserCheck,
  KeyRound,
  DollarSign,
  Activity,
  ShieldAlert
} from 'lucide-react';
import './AdminDashboard.css';

export default function AdminDashboard() {
  const { user: currentAdmin } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('PendingApproval');
  const [actionError, setActionError] = useState(null);
  const [actionSuccess, setActionSuccess] = useState(null);
  const [processingId, setProcessingId] = useState(null);

  // Budget & Usage Monitoring State
  const [budgetUsage, setBudgetUsage] = useState(null);
  const [loadingUsage, setLoadingUsage] = useState(false);

  // Reject Modal State
  const [rejectModalUser, setRejectModalUser] = useState(null);
  const [rejectReason, setRejectReason] = useState('');

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    setActionError(null);
    try {
      const data = await api.admin.getUsers(filter === 'all' ? null : filter);
      setUsers(data);
    } catch (err) {
      setActionError(err.message || 'Failed to fetch user directory.');
    } finally {
      setLoading(false);
    }
  }, [filter]);

  const fetchBudgetUsage = useCallback(async () => {
    setLoadingUsage(true);
    try {
      const usage = await api.admin.getUsageToday();
      setBudgetUsage(usage);
    } catch (err) {
      console.error('Failed to fetch AI budget usage:', err);
    } finally {
      setLoadingUsage(false);
    }
  }, []);

  useEffect(() => {
    fetchUsers();
    fetchBudgetUsage();
  }, [fetchUsers, fetchBudgetUsage]);

  const handleApprove = async (userId, userEmail) => {
    if (!window.confirm(`Approve registration for ${userEmail}?`)) return;

    setProcessingId(userId);
    setActionError(null);
    try {
      const updatedUser = await api.admin.approveUser(userId);
      setUsers((prev) => prev.map((u) => (u.id === userId ? updatedUser : u)));
      setActionSuccess(`User ${userEmail} has been approved and notified.`);
      setTimeout(() => setActionSuccess(null), 4000);
    } catch (err) {
      setActionError(err.message || 'Failed to approve user.');
    } finally {
      setProcessingId(null);
    }
  };

  const handleOpenRejectModal = (user) => {
    setRejectModalUser(user);
    setRejectReason('');
  };

  const handleConfirmReject = async () => {
    if (!rejectModalUser) return;

    setProcessingId(rejectModalUser.id);
    setActionError(null);
    try {
      const updatedUser = await api.admin.rejectUser(rejectModalUser.id, rejectReason.trim() || null);
      setUsers((prev) => prev.map((u) => (u.id === rejectModalUser.id ? updatedUser : u)));
      setActionSuccess(`User ${rejectModalUser.email} has been rejected.`);
      setRejectModalUser(null);
      setTimeout(() => setActionSuccess(null), 4000);
    } catch (err) {
      setActionError(err.message || 'Failed to reject user.');
    } finally {
      setProcessingId(null);
    }
  };

  const handleResetTotp = async (userId, userEmail) => {
    if (
      !window.confirm(
        `Reset TOTP two-factor authentication for ${userEmail}?\n\nThe user will be required to re-enroll with a new QR code on their next login.`
      )
    ) {
      return;
    }

    setProcessingId(userId);
    setActionError(null);
    try {
      await api.admin.resetTotp(userId);
      setActionSuccess(`TOTP 2FA has been reset for ${userEmail}. Re-enrollment will be enforced on their next login.`);
      setTimeout(() => setActionSuccess(null), 5000);
    } catch (err) {
      setActionError(err.message || 'Failed to reset TOTP.');
    } finally {
      setProcessingId(null);
    }
  };

  const percentSpend = budgetUsage
    ? Math.min(100, Math.round((budgetUsage.totalCostTodayUsd / (budgetUsage.dailyCapUsd || 2.0)) * 100))
    : 0;

  return (
    <div className="admin-container">
      {/* Editorial Header */}
      <header className="admin-header">
        <div className="admin-header-main">
          <span className="admin-kicker">Administrative Control</span>
          <h1 className="admin-title">Learner Directory & Operations</h1>
          <p className="admin-subtitle">
            Review user registrations, manage two-factor authentication policies, and monitor shared daily AI compute consumption.
          </p>
        </div>

        <div className="admin-header-actions">
          <button
            type="button"
            onClick={() => {
              fetchUsers();
              fetchBudgetUsage();
            }}
            disabled={loading || loadingUsage}
            className="admin-refresh-btn"
            title="Refresh Directory and Budget"
          >
            <RefreshCw size={15} className={loading || loadingUsage ? 'spinning' : ''} />
            <span>Refresh</span>
          </button>
        </div>
      </header>

      {/* AI Budget & Spend Monitor Card */}
      {budgetUsage && (
        <section className="admin-budget-card" style={{
          background: 'var(--surface-elevated, #FFFFFF)',
          border: '1px solid var(--border-subtle, #E4E0D7)',
          borderRadius: '10px',
          padding: '20px 24px',
          marginBottom: '28px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.03)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <DollarSign size={20} style={{ color: 'var(--accent-sage, #2C5E55)' }} />
              <div>
                <h3 style={{ margin: 0, fontSize: '1.05rem', fontFamily: 'var(--font-heading, Newsreader, serif)' }}>
                  Meta Llama AI Compute Budget
                </h3>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted, #726E65)' }}>
                  Enforced aggregate limit resets at 00:00 UTC
                </span>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <span
                style={{
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  padding: '4px 10px',
                  borderRadius: '12px',
                  background: budgetUsage.budgetExceeded
                    ? '#FCE8E6'
                    : percentSpend >= 80
                    ? '#FEF3D6'
                    : '#E6F4EA',
                  color: budgetUsage.budgetExceeded
                    ? '#C5221F'
                    : percentSpend >= 80
                    ? '#B06000'
                    : '#137333',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px'
                }}
              >
                {budgetUsage.budgetExceeded ? (
                  <>
                    <ShieldAlert size={13} /> Hard Cap Reached (429 Active)
                  </>
                ) : (
                  <>
                    <Activity size={13} /> Spend Active ({percentSpend}%)
                  </>
                )}
              </span>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            <div style={{ padding: '12px 16px', background: 'var(--bg-parchment, #F8F6F0)', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted, #726E65)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Spend Today
              </span>
              <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-primary, #1B1B18)', marginTop: '4px' }}>
                ${budgetUsage.totalCostTodayUsd.toFixed(4)}
              </div>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted, #726E65)' }}>
                Cap: ${budgetUsage.dailyCapUsd.toFixed(2)} / day
              </span>
            </div>

            <div style={{ padding: '12px 16px', background: 'var(--bg-parchment, #F8F6F0)', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted, #726E65)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Total Requests Today
              </span>
              <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-primary, #1B1B18)', marginTop: '4px' }}>
                {budgetUsage.requestCountToday}
              </div>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted, #726E65)' }}>
                Maximum: {budgetUsage.maxDailyRequests} req / day
              </span>
            </div>
          </div>
        </section>
      )}

      {/* Filter Tabs */}
      <div className="admin-filters-bar">
        <button
          type="button"
          className={`filter-chip ${filter === 'PendingApproval' ? 'active' : ''}`}
          onClick={() => setFilter('PendingApproval')}
        >
          <Clock size={14} />
          <span>Pending Approval</span>
          {filter === 'PendingApproval' && <span className="chip-badge">{users.length}</span>}
        </button>

        <button
          type="button"
          className={`filter-chip ${filter === 'Approved' ? 'active' : ''}`}
          onClick={() => setFilter('Approved')}
        >
          <UserCheck size={14} />
          <span>Approved</span>
          {filter === 'Approved' && <span className="chip-badge">{users.length}</span>}
        </button>

        <button
          type="button"
          className={`filter-chip ${filter === 'Rejected' ? 'active' : ''}`}
          onClick={() => setFilter('Rejected')}
        >
          <AlertTriangle size={14} />
          <span>Rejected</span>
          {filter === 'Rejected' && <span className="chip-badge">{users.length}</span>}
        </button>

        <button
          type="button"
          className={`filter-chip ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          <Users size={14} />
          <span>All Accounts</span>
          {filter === 'all' && <span className="chip-badge">{users.length}</span>}
        </button>
      </div>

      {/* Alert Messages */}
      {actionSuccess && (
        <div className="admin-alert success">
          <Check size={16} />
          <span>{actionSuccess}</span>
        </div>
      )}

      {actionError && (
        <div className="admin-alert error">
          <AlertTriangle size={16} />
          <span>{actionError}</span>
        </div>
      )}

      {/* Users Table / List */}
      <section className="admin-table-chamber">
        {loading ? (
          <div className="admin-loading-state">
            <RefreshCw size={24} className="spinning" />
            <p>Loading directory...</p>
          </div>
        ) : users.length === 0 ? (
          <div className="admin-empty-state">
            <Users size={32} className="empty-icon" />
            <h3>No users found</h3>
            <p>
              {filter === 'PendingApproval'
                ? 'There are no pending registrations requiring review at this time.'
                : `No users matched the '${filter}' filter.`}
            </p>
          </div>
        ) : (
          <div className="admin-table-wrapper">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Learner</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Registered</th>
                  <th>Last Active</th>
                  <th className="th-actions">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((item) => (
                  <tr key={item.id} className={`user-row status-${item.status.toLowerCase()}`}>
                    <td className="td-learner">
                      <div className="learner-meta">
                        <span className="learner-name">{item.displayName || 'Anonymous Learner'}</span>
                        <span className="learner-email">{item.email}</span>
                      </div>
                    </td>

                    <td>
                      <span className={`badge-role role-${item.role.toLowerCase()}`}>
                        {item.role}
                      </span>
                    </td>

                    <td>
                      <span className={`badge-status status-${item.status.toLowerCase()}`}>
                        {item.status === 'PendingApproval' ? 'Pending Approval' : item.status}
                      </span>
                    </td>

                    <td className="td-date">
                      {new Date(item.createdAt).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric'
                      })}
                    </td>

                    <td className="td-date">
                      {item.lastLoginAt
                        ? new Date(item.lastLoginAt).toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric'
                          })
                        : 'Never'}
                    </td>

                    <td className="td-actions">
                      {item.status === 'PendingApproval' ? (
                        <div className="actions-cell-group">
                          <button
                            type="button"
                            disabled={processingId === item.id}
                            onClick={() => handleApprove(item.id, item.email)}
                            className="btn-action-approve"
                            title="Approve User"
                          >
                            <Check size={14} />
                            <span>Approve</span>
                          </button>

                          <button
                            type="button"
                            disabled={processingId === item.id}
                            onClick={() => handleOpenRejectModal(item)}
                            className="btn-action-reject"
                            title="Reject User"
                          >
                            <X size={14} />
                            <span>Reject</span>
                          </button>
                        </div>
                      ) : item.status === 'Approved' ? (
                        <div className="actions-cell-group">
                          <button
                            type="button"
                            disabled={processingId === item.id}
                            onClick={() => handleResetTotp(item.id, item.email)}
                            className="btn-action-reset-totp"
                            style={{
                              background: 'none',
                              border: '1px solid var(--border-subtle, #E4E0D7)',
                              color: 'var(--text-secondary, #504D44)',
                              padding: '5px 10px',
                              borderRadius: '6px',
                              fontSize: '0.8rem',
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '5px',
                              cursor: 'pointer'
                            }}
                            title="Reset TOTP 2FA secret"
                          >
                            <KeyRound size={13} />
                            <span>Reset TOTP</span>
                          </button>
                        </div>
                      ) : (
                        <span className="actions-settled-text">
                          Registration Closed
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Reject Reason Modal */}
      {rejectModalUser && (
        <div className="modal-backdrop" onClick={() => setRejectModalUser(null)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Reject Registration</h3>
              <button
                type="button"
                className="modal-close-btn"
                onClick={() => setRejectModalUser(null)}
              >
                <X size={18} />
              </button>
            </div>

            <p className="modal-body-text">
              Rejecting registration for <strong>{rejectModalUser.email}</strong>. The user will be notified of this decision.
            </p>

            <div className="form-group modal-form-group">
              <label htmlFor="reject-reason">Optional Reason for Rejection</label>
              <textarea
                id="reject-reason"
                rows={3}
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                placeholder="e.g. Email domain not permitted, prerequisite review pending..."
              />
            </div>

            <div className="modal-actions">
              <button
                type="button"
                className="btn-secondary"
                onClick={() => setRejectModalUser(null)}
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={processingId === rejectModalUser.id}
                className="btn-danger"
                onClick={handleConfirmReject}
              >
                {processingId === rejectModalUser.id ? 'Processing...' : 'Confirm Rejection'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
