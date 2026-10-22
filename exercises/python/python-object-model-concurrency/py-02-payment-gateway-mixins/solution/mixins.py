class LoggingMixin:
    def log_action(self, action):
        print(f"[LOG] {self.__class__.__name__}: {action}")


class AuditMixin:
    def __init__(self, **kwargs):
        self.audit_trail = []
        super().__init__(**kwargs)

    def record_audit(self, event):
        self.audit_trail.append(event)
