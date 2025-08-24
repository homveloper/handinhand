using Microsoft.AspNetCore.Mvc;
using Swashbuckle.AspNetCore.Annotations;
using HandInHand.Server.Api.Models;
using HandInHand.Domain.User.Entities;
using HandInHand.Server.Infrastructure;
using HandInHand.Server.Domain;

namespace HandInHand.Server.Api.Controllers;

[ApiController]
[Route("api/inventory")]
[Tags("InventoryManagement")]
public class InventoryController : ControllerBase
{
    private readonly FindOneAndUpdateFunc<UserAggregatesSchema> _updateUser;
    private readonly FindOneFunc<UserAggregatesSchema> _findUser;

    public InventoryController(
        FindOneAndUpdateFunc<UserAggregatesSchema> updateUser,
        FindOneFunc<UserAggregatesSchema> findUser)
    {
        _updateUser = updateUser;
        _findUser = findUser;
    }

    [HttpPost("addGold")]
    [SwaggerOperation(
        Summary = "Add gold to inventory",
        Description = "Adds gold to user's inventory with validation"
    )]
    [SwaggerResponse(200, "Gold added successfully")]
    [SwaggerResponse(400, "Invalid gold amount")]
    public async Task<IActionResult> AddGold([FromBody] JsonRpcRequest<AddGoldParams> request)
    {
        (UserAggregatesSchema? user, string? error) = await _updateUser(
            request.Params.UserId,
            // updateFn: 골드 추가 로직 (도메인 함수 사용)
            (existing, _) => existing with
            {
                Inventory = Inventory.AddGold(existing.Inventory, request.Params.Gold)
            }
        );

        return error != null
            ? BadRequest(CreateErrorResponse(-32001, $"ADD_GOLD_FAILED: {error}"))
            : Ok(CreateSuccessResponse(new { 
                userId = request.Params.UserId,
                newGoldAmount = user?.Inventory.Gold,
                addedAmount = request.Params.Gold
            }));
    }

    [HttpPost("getInventory")]
    [SwaggerOperation(
        Summary = "Get user inventory",
        Description = "Retrieves user's complete inventory including items and gold"
    )]
    [SwaggerResponse(200, "Inventory retrieved successfully")]
    [SwaggerResponse(404, "User not found")]
    public async Task<IActionResult> GetInventory([FromBody] JsonRpcRequest<GetInventoryParams> request)
    {
        (UserAggregatesSchema? user, string? error) = await _findUser(request.Params.UserId);

        return error != null
            ? NotFound(CreateErrorResponse(-32001, $"USER_NOT_FOUND: {error}"))
            : Ok(CreateSuccessResponse(user?.Inventory));
    }

    [HttpPost("addItem")]
    [SwaggerOperation(
        Summary = "Add item to inventory",
        Description = "Adds an item to user's inventory or increases quantity if it exists"
    )]
    [SwaggerResponse(200, "Item added successfully")]
    [SwaggerResponse(400, "Invalid item or inventory full")]
    public async Task<IActionResult> AddItem([FromBody] JsonRpcRequest<AddItemParams> request)
    {
        (UserAggregatesSchema? user, string? error) = await _updateUser(
            request.Params.UserId,
            // updateFn: 아이템 추가 로직 (도메인 함수 사용)
            (existing, _) => existing with
            {
                Inventory = Inventory.AddItem(
                    existing.Inventory, 
                    request.Params.ItemId, 
                    request.Params.Quantity,
                    request.Params.Rarity)
            }
        );

        return error != null
            ? BadRequest(CreateErrorResponse(-32001, $"ADD_ITEM_FAILED: {error}"))
            : Ok(CreateSuccessResponse(user?.Inventory));
    }

    [HttpPost("removeItem")]
    [SwaggerOperation(
        Summary = "Remove item from inventory",
        Description = "Removes an item from user's inventory or decreases quantity"
    )]
    [SwaggerResponse(200, "Item removed successfully")]
    [SwaggerResponse(400, "Item not found or invalid quantity")]
    public async Task<IActionResult> RemoveItem([FromBody] JsonRpcRequest<RemoveItemParams> request)
    {
        (UserAggregatesSchema? user, string? error) = await _updateUser(
            request.Params.UserId,
            // updateFn: 아이템 제거 로직 (도메인 함수 사용)
            (existing, _) => existing with
            {
                Inventory = Inventory.RemoveItem(
                    existing.Inventory, 
                    request.Params.ItemId, 
                    request.Params.Quantity)
            }
        );

        return error != null
            ? BadRequest(CreateErrorResponse(-32001, $"REMOVE_ITEM_FAILED: {error}"))
            : Ok(CreateSuccessResponse(user?.Inventory));
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
public class AddGoldParams
{
    public string UserId { get; set; } = "";
    public long Gold { get; set; }
}

public class GetInventoryParams
{
    public string UserId { get; set; } = "";
}

public class AddItemParams
{
    public string UserId { get; set; } = "";
    public string ItemId { get; set; } = "";
    public long Quantity { get; set; } = 1;
    public string? Rarity { get; set; }
}

public class RemoveItemParams
{
    public string UserId { get; set; } = "";
    public string ItemId { get; set; } = "";
    public long Quantity { get; set; } = 1;
}