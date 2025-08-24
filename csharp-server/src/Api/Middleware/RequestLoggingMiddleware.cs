using System.Diagnostics;

namespace HandInHand.Server.Api.Middleware;

public class RequestLoggingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<RequestLoggingMiddleware> _logger;

    public RequestLoggingMiddleware(RequestDelegate next, ILogger<RequestLoggingMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        var stopwatch = Stopwatch.StartNew();
        var requestId = Guid.NewGuid().ToString()[..8];
        
        // 요청 로깅
        _logger.LogInformation(
            "[{RequestId}] {Method} {Path} - Started",
            requestId,
            context.Request.Method,
            context.Request.Path
        );

        try
        {
            await _next(context);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, 
                "[{RequestId}] {Method} {Path} - Error: {Error}",
                requestId,
                context.Request.Method,
                context.Request.Path,
                ex.Message
            );
            throw;
        }
        finally
        {
            stopwatch.Stop();
            
            // 응답 로깅
            _logger.LogInformation(
                "[{RequestId}] {Method} {Path} - Completed in {ElapsedMs}ms with status {StatusCode}",
                requestId,
                context.Request.Method,
                context.Request.Path,
                stopwatch.ElapsedMilliseconds,
                context.Response.StatusCode
            );
        }
    }
}