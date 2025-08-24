using Microsoft.AspNetCore.Mvc;
using Swashbuckle.AspNetCore.Annotations;
using HandInHand.Server.Api.Models;

namespace HandInHand.Server.Api.Controllers;

/// <summary>
/// 🔧 시스템 API 컨트롤러
/// 서버 상태 확인 및 시스템 관리 기능
/// </summary>
[ApiController]
[Route("api/system")]
[Produces("application/json")]
[Tags("SystemManagement")]
public class SystemController : ControllerBase
{
    private readonly ILogger<SystemController> _logger;

    public SystemController(ILogger<SystemController> logger)
    {
        _logger = logger;
    }

    /// <summary>
    /// 서버 상태 확인 (헬스체크)
    /// </summary>
    /// <returns>서버 상태 정보</returns>
    [HttpGet("health")]
    [SwaggerOperation(
        Summary = "서버 헬스체크",
        Description = "서버의 상태와 기본 정보를 조회합니다. 로드밸런서에서 사용됩니다."
    )]
    [SwaggerResponse(200, "서버 정상", typeof(object))]
    public ActionResult GetHealth()
    {
        var healthInfo = new
        {
            status = "ok",
            server = "csharp-hybrid", 
            timestamp = DateTimeOffset.UtcNow,
            version = "1.0.0",
            uptime = Environment.TickCount64 / 1000, // seconds
            architecture = "REST+JSON-RPC Hybrid"
        };

        return Ok(healthInfo);
    }

    /// <summary>
    /// 서버 정보 조회
    /// </summary>
    /// <param name="request">서버 정보 요청</param>
    /// <returns>서버 상세 정보</returns>
    [HttpPost("getServerInfo")]
    [SwaggerOperation(
        Summary = "서버 정보 조회",
        Description = "서버의 상세 정보와 API 엔드포인트 목록을 조회합니다."
    )]
    [SwaggerResponse(200, "조회 성공", typeof(JsonRpcResponse<object>))]
    public ActionResult<JsonRpcResponse<object>> GetServerInfo(
        [FromBody, SwaggerRequestBody("서버 정보 조회 요청")] 
        JsonRpcRequest<object> request)
    {
        var serverInfo = new
        {
            name = "Hand in Hand C# Server",
            version = "1.0.0",
            architecture = "DDD + REST + JSON-RPC Hybrid",
            framework = "ASP.NET Core 8.0",
            database = "Redis",
            endpoints = new
            {
                user = new[]
                {
                    "POST /api/user/getUserAggregates",
                    "POST /api/user/createUser",
                    "POST /api/user/addUserExp",
                    "POST /api/user/addUserGold",
                    "POST /api/user/updateUserNickname"
                },
                character = new[]
                {
                    "POST /api/character/addExp",
                    "POST /api/character/getProfile"
                },
                inventory = new[]
                {
                    "POST /api/inventory/addGold",
                    "POST /api/inventory/getInventory"
                },
                system = new[]
                {
                    "GET /api/system/health",
                    "POST /api/system/getServerInfo"
                }
            },
            features = new[]
            {
                "REST URL + JSON-RPC Body",
                "Swagger UI Documentation", 
                "Automatic OpenRPC Generation",
                "Server-Sent Events (SSE)",
                "Redis Optimistic Concurrency Control",
                "Structured Logging with Serilog"
            }
        };

        return Ok(JsonRpcResponse<object>.Success(serverInfo, request.Id));
    }
}