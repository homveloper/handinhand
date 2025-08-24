using System.Net;
using System.Text.Json;
using System.Security;
using HandInHand.Server.Api.Models;

namespace HandInHand.Server.Api.Middleware;

/// <summary>
/// 글로벌 예외 처리 미들웨어 (Go의 recover() 역할)
/// - 패닉 복구 (Panic Recovery)
/// - DB 에러 어댑팅 (Error Adapting) 
/// - 보안 에러 마스킹 (Error Masking)
/// </summary>
public class GlobalExceptionHandlingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<GlobalExceptionHandlingMiddleware> _logger;
    private readonly IWebHostEnvironment _environment;

    public GlobalExceptionHandlingMiddleware(
        RequestDelegate next,
        ILogger<GlobalExceptionHandlingMiddleware> logger,
        IWebHostEnvironment environment)
    {
        _next = next;
        _logger = logger;
        _environment = environment;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await _next(context);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, 
                "🚨 Unhandled exception occurred. RequestId: {RequestId}, Path: {Path}, Method: {Method}",
                context.TraceIdentifier,
                context.Request.Path,
                context.Request.Method);

            await HandleExceptionAsync(context, ex);
        }
    }

    private async Task HandleExceptionAsync(HttpContext context, Exception exception)
    {
        context.Response.ContentType = "application/json";

        // 🔄 Exception을 Error Response로 변환 (Error Adapting)
        var errorResponse = AdaptExceptionToErrorResponse(exception, context);
        
        context.Response.StatusCode = errorResponse.StatusCode;

        var jsonResponse = JsonSerializer.Serialize(errorResponse.Response, new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            WriteIndented = _environment.IsDevelopment()
        });

        await context.Response.WriteAsync(jsonResponse);
    }

    /// <summary>
    /// 🛡️ Exception을 안전한 Error Response로 변환 (Go의 error wrapping과 유사)
    /// </summary>
    private ErrorResponseInfo AdaptExceptionToErrorResponse(Exception exception, HttpContext context)
    {
        var requestId = GetRequestId(context);
        
        return exception switch
        {
            // === 🗄️ Redis 관련 에러들 (DB Error Adapting) === //
            StackExchange.Redis.RedisException redisEx
                => CreateErrorResponse(
                    HttpStatusCode.InternalServerError,
                    -32603,
                    "DATABASE_ERROR: Database operation failed",
                    $"Redis error: {redisEx.GetType().Name}",
                    requestId),

            // === ⏱️ 타임아웃 관련 에러들 === //
            TimeoutException
                => CreateErrorResponse(
                    HttpStatusCode.RequestTimeout,
                    -32603,
                    "TIMEOUT: Operation timed out",
                    "Request processing timeout",
                    requestId),

            OperationCanceledException when context.RequestAborted.IsCancellationRequested
                => CreateErrorResponse(
                    (HttpStatusCode)499, // Client Closed Request
                    -32603,
                    "CANCELLED: Request was cancelled by client",
                    "Client disconnected",
                    requestId),

            OperationCanceledException
                => CreateErrorResponse(
                    HttpStatusCode.RequestTimeout,
                    -32603,
                    "CANCELLED: Operation was cancelled",
                    "Server-side cancellation",
                    requestId),

            // === 🔒 보안 관련 에러들 (Security Error Masking) === //
            UnauthorizedAccessException
                => CreateErrorResponse(
                    HttpStatusCode.Unauthorized,
                    -32001,
                    "UNAUTHORIZED: Access denied",
                    "Authentication required",
                    requestId),

            SecurityException
                => CreateErrorResponse(
                    HttpStatusCode.Forbidden,
                    -32001,
                    "FORBIDDEN: Insufficient permissions",
                    "Authorization failed",
                    requestId),

            // === 📝 Validation 관련 에러들 === //
            ArgumentNullException argNullEx
                => CreateErrorResponse(
                    HttpStatusCode.BadRequest,
                    -32602,
                    $"INVALID_INPUT: {argNullEx.ParamName} is required",
                    "Parameter validation failed",
                    requestId),

            ArgumentException argEx
                => CreateErrorResponse(
                    HttpStatusCode.BadRequest,
                    -32602,
                    $"INVALID_INPUT: {argEx.Message}",
                    "Argument validation failed",
                    requestId),

            FormatException
                => CreateErrorResponse(
                    HttpStatusCode.BadRequest,
                    -32602,
                    "INVALID_INPUT: Invalid data format",
                    "Data format validation failed",
                    requestId),

            // === 🌐 HTTP 관련 에러들 === //
            HttpRequestException httpEx
                => CreateErrorResponse(
                    HttpStatusCode.BadGateway,
                    -32603,
                    "EXTERNAL_ERROR: External service call failed",
                    $"HTTP error: {httpEx.Message}",
                    requestId),

            // === 🚨 시스템 관련 Critical 에러들 === //
            OutOfMemoryException
                => CreateErrorResponse(
                    HttpStatusCode.InternalServerError,
                    -32603,
                    "SYSTEM_ERROR: Insufficient memory",
                    "Critical system error - memory",
                    requestId),

            StackOverflowException
                => CreateErrorResponse(
                    HttpStatusCode.InternalServerError,
                    -32603,
                    "SYSTEM_ERROR: Stack overflow occurred",
                    "Critical system error - stack",
                    requestId),

            // === 🏗️ 커스텀 비즈니스 에러들 === //
            DomainException domainEx
                => CreateErrorResponse(
                    HttpStatusCode.BadRequest,
                    domainEx.ErrorCode,
                    domainEx.Message,
                    "Business rule validation failed",
                    requestId),

            // === 🔧 개발/디버그 관련 === //
            NotImplementedException
                => CreateErrorResponse(
                    HttpStatusCode.NotImplemented,
                    -32601,
                    "NOT_IMPLEMENTED: Feature not yet implemented",
                    "Development in progress",
                    requestId),

            // === 🛡️ 기본 Fallback (모든 예상치 못한 에러들) === //
            _ => CreateErrorResponse(
                HttpStatusCode.InternalServerError,
                -32603,
                "INTERNAL_ERROR: An unexpected error occurred",
                GetSafeErrorMessage(exception), // 🔒 민감한 정보 필터링
                requestId)
        };
    }

    /// <summary>
    /// 🔒 민감한 정보를 제거한 안전한 에러 메시지 생성
    /// </summary>
    private string GetSafeErrorMessage(Exception exception)
    {
        if (_environment.IsDevelopment())
        {
            // 개발 환경: 상세 에러 정보 제공
            return $"{exception.GetType().Name}: {exception.Message}";
        }

        // 운영 환경: 민감한 정보 제거
        var safeMessage = exception.GetType().Name;
        
        // 특정 안전한 메시지들만 포함
        var safeMessages = new[]
        {
            "validation", "format", "argument", "parameter", 
            "invalid", "required", "empty", "null"
        };

        if (safeMessages.Any(safe => exception.Message.ToLower().Contains(safe)))
        {
            safeMessage += $": {exception.Message}";
        }

        return safeMessage;
    }

    private ErrorResponseInfo CreateErrorResponse(
        HttpStatusCode statusCode,
        int jsonRpcCode,
        string publicMessage,
        string logMessage,
        string requestId)
    {
        // 🔍 로깅용 추가 정보
        _logger.LogWarning(
            "Error adapted - Status: {StatusCode}, JsonRpcCode: {JsonRpcCode}, " +
            "LogMessage: {LogMessage}, RequestId: {RequestId}",
            (int)statusCode, jsonRpcCode, logMessage, requestId);

        var response = new JsonRpcResponse<object>
        {
            JsonRpc = "2.0",
            Error = new JsonRpcError
            {
                Code = jsonRpcCode,
                Message = publicMessage,
                Data = _environment.IsDevelopment() ? new
                {
                    requestId = requestId,
                    timestamp = DateTimeOffset.UtcNow,
                    logMessage = logMessage
                } : new
                {
                    requestId = requestId,
                    timestamp = DateTimeOffset.UtcNow
                }
            },
            Id = requestId
        };

        return new ErrorResponseInfo
        {
            StatusCode = (int)statusCode,
            Response = response
        };
    }

    private string GetRequestId(HttpContext context)
    {
        // JSON-RPC request에서 ID 추출 시도
        if (context.Items.ContainsKey("JsonRpcRequestId"))
        {
            return context.Items["JsonRpcRequestId"]?.ToString() ?? context.TraceIdentifier;
        }

        return context.TraceIdentifier;
    }

    private record ErrorResponseInfo
    {
        public int StatusCode { get; init; }
        public object Response { get; init; } = null!;
    }
}

/// <summary>
/// 커스텀 도메인 예외 클래스
/// </summary>
public class DomainException : Exception
{
    public int ErrorCode { get; }

    public DomainException(string message, int errorCode = -32001) : base(message)
    {
        ErrorCode = errorCode;
    }

    public DomainException(string message, Exception innerException, int errorCode = -32001) 
        : base(message, innerException)
    {
        ErrorCode = errorCode;
    }
}