using Microsoft.AspNetCore.Mvc;
using Swashbuckle.AspNetCore.Annotations;
using HandInHand.Server.Api.Models;
using HandInHand.Domain.User.Entities;
using HandInHand.Server.Infrastructure;
using HandInHand.Server.Domain;

namespace HandInHand.Server.Api.Controllers;

[ApiController]
[Route("api/user")]
[Tags("UserManagement")]
public class UserController : ControllerBase
{
    private readonly FindOneAndUpsertFunc<UserAggregatesSchema> _upsertUser;
    private readonly FindOneFunc<UserAggregatesSchema> _findUser;
    private readonly FindOneAndUpdateFunc<UserAggregatesSchema> _updateUser;

    public UserController(
        FindOneAndUpsertFunc<UserAggregatesSchema> upsertUser,
        FindOneFunc<UserAggregatesSchema> findUser,
        FindOneAndUpdateFunc<UserAggregatesSchema> updateUser)
    {
        _upsertUser = upsertUser;
        _findUser = findUser;
        _updateUser = updateUser;
    }

    [HttpPost("createUser")]
    [SwaggerOperation(
        Summary = "Create a new user",
        Description = "Creates a new user with profile and inventory. User ID must be unique."
    )]
    [SwaggerResponse(201, "User created successfully")]
    [SwaggerResponse(409, "User already exists")]
    public async Task<IActionResult> CreateUser([FromBody] JsonRpcRequest<CreateUserParams> request)
    {
        (UserAggregatesSchema? user, string? error) = await _upsertUser(
            request.Params.UserId,
            // createFn: 새 사용자 생성 로직
            userId => HandInHand.Server.Domain.User.CreateNewUser(userId, request.Params.Nickname),
            // updateFn: 이미 존재하면 에러
            (existing, _) => throw new InvalidOperationException($"User {request.Params.UserId} already exists")
        );

        return error != null
            ? Conflict(CreateErrorResponse(-32001, $"CREATE_USER_FAILED: {error}"))
            : Created("", CreateSuccessResponse(user));
    }

    [HttpPost("getUserAggregates")]
    [SwaggerOperation(
        Summary = "Get complete user data",
        Description = "Retrieves complete user aggregates including profile and inventory"
    )]
    [SwaggerResponse(200, "User data retrieved successfully")]
    [SwaggerResponse(404, "User not found")]
    public async Task<IActionResult> GetUserAggregates([FromBody] JsonRpcRequest<GetUserParams> request)
    {
        var (user, error) = await _findUser(request.Params.UserId);

        return error != null
            ? NotFound(CreateErrorResponse(-32001, $"USER_NOT_FOUND: {error}"))
            : Ok(CreateSuccessResponse(user));
    }

    [HttpPost("addUserExp")]
    [SwaggerOperation(
        Summary = "Add experience to user",
        Description = "Adds experience points to user profile. Automatic level up when enough exp."
    )]
    [SwaggerResponse(200, "Experience added successfully")]
    [SwaggerResponse(400, "Invalid experience amount")]
    public async Task<IActionResult> AddUserExp([FromBody] JsonRpcRequest<AddUserExpParams> request)
    {
        (UserAggregatesSchema? user, string? error) = await _updateUser(
            request.Params.UserId,
            // updateFn: 경험치 추가 로직 (도메인 함수 사용)
            (existing, _) => HandInHand.Server.Domain.User.AddUserExp(existing, request.Params.Exp)
        );

        return error != null
            ? BadRequest(CreateErrorResponse(-32001, $"ADD_USER_EXP_FAILED: {error}"))
            : Ok(CreateSuccessResponse(user));
    }

    [HttpPost("addUserGold")]
    [SwaggerOperation(
        Summary = "Add gold to user inventory",
        Description = "Adds gold to user's inventory"
    )]
    [SwaggerResponse(200, "Gold added successfully")]
    [SwaggerResponse(400, "Invalid gold amount")]
    public async Task<IActionResult> AddUserGold([FromBody] JsonRpcRequest<AddUserGoldParams> request)
    {
        (UserAggregatesSchema? user, string? error) = await _updateUser(
            request.Params.UserId,
            // updateFn: 골드 추가 로직 (도메인 함수 사용)
            (existing, _) => HandInHand.Server.Domain.User.AddGold(existing, request.Params.Gold)
        );

        return error != null
            ? BadRequest(CreateErrorResponse(-32001, $"ADD_USER_GOLD_FAILED: {error}"))
            : Ok(CreateSuccessResponse(user));
    }

    [HttpPost("updateUserNickname")]
    [SwaggerOperation(
        Summary = "Update user nickname",
        Description = "Updates user's display nickname"
    )]
    [SwaggerResponse(200, "Nickname updated successfully")]
    [SwaggerResponse(400, "Invalid nickname")]
    public async Task<IActionResult> UpdateUserNickname([FromBody] JsonRpcRequest<UpdateNicknameParams> request)
    {
        (UserAggregatesSchema? user, string? error) = await _updateUser(
            request.Params.UserId,
            // updateFn: 닉네임 업데이트 로직 (도메인 함수 사용)
            (existing, _) => HandInHand.Server.Domain.User.UpdateNickname(existing, request.Params.NewNickname)
        );

        return error != null
            ? BadRequest(CreateErrorResponse(-32001, $"UPDATE_NICKNAME_FAILED: {error}"))
            : Ok(CreateSuccessResponse(user));
    }

    private JsonRpcResponse<object> CreateErrorResponse(int code, string message)
    {
        return new JsonRpcResponse<object>
        {
            JsonRpc = "2.0",
            Error = new JsonRpcError { Code = code, Message = message },
            Id = null
        };
    }

    private JsonRpcResponse<T> CreateSuccessResponse<T>(T result)
    {
        return new JsonRpcResponse<T>
        {
            JsonRpc = "2.0",
            Result = result,
            Id = null
        };
    }
}

// Request parameter classes
public class CreateUserParams
{
    public string UserId { get; set; } = "";
    public string? Nickname { get; set; }
}

public class GetUserParams
{
    public string UserId { get; set; } = "";
}

public class AddUserExpParams
{
    public string UserId { get; set; } = "";
    public int Exp { get; set; }
}

public class AddUserGoldParams
{
    public string UserId { get; set; } = "";
    public long Gold { get; set; }
}

public class UpdateNicknameParams
{
    public string UserId { get; set; } = "";
    public string NewNickname { get; set; } = "";
}