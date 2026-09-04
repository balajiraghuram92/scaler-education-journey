using System.Threading;
using System.Threading.Tasks;
using StudyTracker.Api.Models;

namespace StudyTracker.Api.Services.Email;

public interface IEmailNotificationService
{
    Task SendAdminNewUserAlertAsync(AppUser newUser, CancellationToken ct = default);
    Task SendUserPendingConfirmationAsync(AppUser newUser, CancellationToken ct = default);
    Task SendUserApprovedNoticeAsync(AppUser user, CancellationToken ct = default);
    Task SendUserRejectedNoticeAsync(AppUser user, string? reason, CancellationToken ct = default);
}
