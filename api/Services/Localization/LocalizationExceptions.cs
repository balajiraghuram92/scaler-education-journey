using System;

namespace StudyTracker.Api.Services.Localization;

public class LocalizationProjectNotFoundException : Exception
{
    public LocalizationProjectNotFoundException(string slug)
        : base($"Localization project '{slug}' was not found.")
    {
        Slug = slug;
    }

    public string Slug { get; }
}

public class LocalizationStringNotFoundException : Exception
{
    public LocalizationStringNotFoundException(int stringId)
        : base($"Localization string with ID {stringId} was not found.")
    {
        StringId = stringId;
    }

    public int StringId { get; }
}

public class WorkflowStepNotFoundException : Exception
{
    public WorkflowStepNotFoundException(int stepId)
        : base($"Workflow step with ID {stepId} was not found.")
    {
        StepId = stepId;
    }

    public int StepId { get; }
}

public class WorkflowStepBoundaryException : Exception
{
    public WorkflowStepBoundaryException(string message)
        : base(message)
    {
    }
}

public class MarketplaceJobNotFoundException : Exception
{
    public MarketplaceJobNotFoundException(int jobId)
        : base($"Marketplace job with ID {jobId} was not found.")
    {
        JobId = jobId;
    }

    public int JobId { get; }
}

public class MarketplaceBidNotFoundException : Exception
{
    public MarketplaceBidNotFoundException(int bidId)
        : base($"Marketplace bid with ID {bidId} was not found.")
    {
        BidId = bidId;
    }

    public int BidId { get; }
}

public class VendorNotFoundException : Exception
{
    public VendorNotFoundException(int vendorId)
        : base($"Vendor with ID {vendorId} was not found.")
    {
        VendorId = vendorId;
    }

    public int VendorId { get; }
}

public class ProviderNotFoundException : Exception
{
    public ProviderNotFoundException(string provider)
        : base($"Provider '{provider}' was not found.")
    {
        Provider = provider;
    }

    public string Provider { get; }
}

public class InvalidJobStateException : Exception
{
    public InvalidJobStateException(string message)
        : base(message)
    {
    }
}

public class LocalizationLocaleNotFoundException : Exception
{
    public LocalizationLocaleNotFoundException(string localeCode)
        : base($"Localization locale '{localeCode}' was not found.")
    {
        LocaleCode = localeCode;
    }

    public string LocaleCode { get; }
}

public class LocalizationAiDisabledException : Exception
{
    public LocalizationAiDisabledException(string projectSlug)
        : base($"AI assistance is switched off for project '{projectSlug}'.")
    {
        ProjectSlug = projectSlug;
    }

    public string ProjectSlug { get; }
}

public class LocalizationUsageCapReachedException : Exception
{
    public LocalizationUsageCapReachedException(string kind, long used, long limit)
        : base($"Monthly {kind} cap reached ({used} of {limit}).")
    {
        Kind = kind;
        Used = used;
        Limit = limit;
    }

    public string Kind { get; }

    public long Used { get; }

    public long Limit { get; }
}

public class VendorLanguageMismatchException : Exception
{
    public VendorLanguageMismatchException(int vendorId, string localeCode)
        : base($"Vendor with ID {vendorId} does not support locale '{localeCode}'.")
    {
        VendorId = vendorId;
        LocaleCode = localeCode;
    }

    public int VendorId { get; }

    public string LocaleCode { get; }
}
