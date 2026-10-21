class LoggingMixin:
    """``log_action(action)`` prints ``[LOG] ClassName: action`` (ClassName is the runtime class of ``self``)."""

    def log_action(self, action):
        raise NotImplementedError("Implement LoggingMixin.log_action")


class AuditMixin:
    """Keeps an ``audit_trail`` list per instance.

    - ``__init__(self, **kwargs)`` creates ``self.audit_trail = []`` and continues the cooperative
      chain with ``super().__init__(**kwargs)``.
    - ``record_audit(event)`` appends ``event`` to ``audit_trail``.
    """

    def __init__(self, **kwargs):
        raise NotImplementedError("Implement AuditMixin.__init__")

    def record_audit(self, event):
        raise NotImplementedError("Implement AuditMixin.record_audit")
