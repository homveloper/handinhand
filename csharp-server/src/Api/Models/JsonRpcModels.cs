using System.Text.Json.Serialization;

namespace HandInHand.Server.Api.Models;

/// <summary>
/// 하이브리드 REST+JSON-RPC 요청 모델
/// </summary>
/// <typeparam name="T">파라미터 타입</typeparam>
public class JsonRpcRequest<T>
{
    [JsonPropertyName("jsonrpc")]
    public string JsonRpc { get; set; } = "2.0";

    [JsonPropertyName("params")]
    public T Params { get; set; } = default!;

    [JsonPropertyName("id")]
    public object? Id { get; set; }
}

/// <summary>
/// 하이브리드 REST+JSON-RPC 응답 모델
/// </summary>
/// <typeparam name="T">결과 타입</typeparam>
public class JsonRpcResponse<T>
{
    [JsonPropertyName("jsonrpc")]
    public string JsonRpc { get; set; } = "2.0";

    [JsonPropertyName("result")]
    public T? Result { get; set; }

    [JsonPropertyName("error")]
    public JsonRpcError? Error { get; set; }

    [JsonPropertyName("id")]
    public object? Id { get; set; }

    public static JsonRpcResponse<T> Success(T result, object? id = null)
    {
        return new JsonRpcResponse<T>
        {
            Result = result,
            Id = id
        };
    }

    public static JsonRpcResponse<T> Failure(int code, string message, object? id = null)
    {
        return new JsonRpcResponse<T>
        {
            Error = new JsonRpcError { Code = code, Message = message },
            Id = id
        };
    }
}

/// <summary>
/// JSON-RPC 에러 정보
/// </summary>
public class JsonRpcError
{
    [JsonPropertyName("code")]
    public int Code { get; set; }

    [JsonPropertyName("message")]
    public string Message { get; set; } = "";

    [JsonPropertyName("data")]
    public object? Data { get; set; }
}

// === API 파라미터 모델들 === //

/// <summary>
/// 사용자 조회 파라미터
/// </summary>
public class GetUserParams
{
    /// <summary>조회할 사용자 ID</summary>
    public string UserId { get; set; } = "";
}

/// <summary>
/// 사용자 생성 파라미터
/// </summary>
public class CreateUserParams
{
    /// <summary>생성할 사용자 ID</summary>
    public string UserId { get; set; } = "";
    
    /// <summary>사용자 닉네임 (선택사항)</summary>
    public string? Nickname { get; set; }
}

/// <summary>
/// 경험치 추가 파라미터
/// </summary>
public class AddUserExpParams
{
    /// <summary>사용자 ID</summary>
    public string UserId { get; set; } = "";
    
    /// <summary>추가할 경험치</summary>
    public long Exp { get; set; }
}

/// <summary>
/// 골드 추가 파라미터
/// </summary>
public class AddUserGoldParams
{
    /// <summary>사용자 ID</summary>
    public string UserId { get; set; } = "";
    
    /// <summary>추가할 골드</summary>
    public long Gold { get; set; }
}

/// <summary>
/// 닉네임 변경 파라미터
/// </summary>
public class UpdateUserNicknameParams
{
    /// <summary>사용자 ID</summary>
    public string UserId { get; set; } = "";
    
    /// <summary>새로운 닉네임</summary>
    public string Nickname { get; set; } = "";
}