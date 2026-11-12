"""Ported from api/Services/Localization/LocalizationExceptions.cs."""

from __future__ import annotations


class LocalizationProjectNotFoundException(Exception):
    def __init__(self, slug: str) -> None:
        super().__init__(f"Localization project '{slug}' was not found.")
        self.slug = slug


class LocalizationStringNotFoundException(Exception):
    def __init__(self, string_id: int) -> None:
        super().__init__(f"Localization string with ID {string_id} was not found.")
        self.string_id = string_id


class WorkflowStepNotFoundException(Exception):
    def __init__(self, step_id: int) -> None:
        super().__init__(f"Workflow step with ID {step_id} was not found.")
        self.step_id = step_id


class WorkflowStepBoundaryException(Exception):
    pass


class MarketplaceJobNotFoundException(Exception):
    def __init__(self, job_id: int) -> None:
        super().__init__(f"Marketplace job with ID {job_id} was not found.")
        self.job_id = job_id


class MarketplaceBidNotFoundException(Exception):
    def __init__(self, bid_id: int) -> None:
        super().__init__(f"Marketplace bid with ID {bid_id} was not found.")
        self.bid_id = bid_id


class VendorNotFoundException(Exception):
    def __init__(self, vendor_id: int) -> None:
        super().__init__(f"Vendor with ID {vendor_id} was not found.")
        self.vendor_id = vendor_id


class ProviderNotFoundException(Exception):
    def __init__(self, provider: str) -> None:
        super().__init__(f"Provider '{provider}' was not found.")
        self.provider = provider


class InvalidJobStateException(Exception):
    pass


class LocalizationLocaleNotFoundException(Exception):
    def __init__(self, locale_code: str) -> None:
        super().__init__(f"Localization locale '{locale_code}' was not found.")
        self.locale_code = locale_code


class LocalizationAiDisabledException(Exception):
    def __init__(self, project_slug: str) -> None:
        super().__init__(
            f"AI assistance is switched off for project '{project_slug}'."
        )
        self.project_slug = project_slug


class LocalizationUsageCapReachedException(Exception):
    def __init__(self, kind: str, used: int, limit: int) -> None:
        super().__init__(f"Monthly {kind} cap reached ({used} of {limit}).")
        self.kind = kind
        self.used = used
        self.limit = limit


class VendorLanguageMismatchException(Exception):
    def __init__(self, vendor_id: int, locale_code: str) -> None:
        super().__init__(
            f"Vendor with ID {vendor_id} does not support locale '{locale_code}'."
        )
        self.vendor_id = vendor_id
        self.locale_code = locale_code
