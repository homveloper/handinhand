using System.Collections.Concurrent;
using System.Text.Json;

namespace HandInHand.Server.Api.SSE;

public interface ISseEventService
{
    Task AddClientAsync(string userId, HttpContext context);
    Task RemoveClientAsync(string userId, string clientId);
    Task BroadcastToUserAsync(string userId, object eventData);
    Task BroadcastToAllAsync(object eventData);
    Task SendHeartbeatAsync();
}

public class SseEventService : ISseEventService
{
    private readonly ConcurrentDictionary<string, List<SseClient>> _userClients = new();
    private readonly ConcurrentDictionary<string, SseClient> _allClients = new();
    private readonly ILogger<SseEventService> _logger;

    public SseEventService(ILogger<SseEventService> logger)
    {
        _logger = logger;
    }

    public async Task AddClientAsync(string userId, HttpContext context)
    {
        var clientId = Guid.NewGuid().ToString();
        var client = new SseClient
        {
            Id = clientId,
            UserId = userId,
            Context = context,
            ConnectedAt = DateTimeOffset.UtcNow
        };

        // 사용자별 클라이언트 목록에 추가
        _userClients.AddOrUpdate(
            userId,
            new List<SseClient> { client },
            (key, existing) =>
            {
                existing.Add(client);
                return existing;
            }
        );

        // 전체 클라이언트 목록에도 추가
        _allClients.TryAdd(clientId, client);

        _logger.LogInformation("SSE client {ClientId} connected for user {UserId}", clientId, userId);

        // 연결 확인 이벤트 전송
        await SendEventToClientAsync(client, new
        {
            type = "connected",
            clientId = clientId,
            userId = userId,
            timestamp = DateTimeOffset.UtcNow,
            serverId = "csharp-server"
        });
    }

    public async Task RemoveClientAsync(string userId, string clientId)
    {
        // 전체 클라이언트 목록에서 제거
        if (_allClients.TryRemove(clientId, out var client))
        {
            // 사용자별 클라이언트 목록에서도 제거
            if (_userClients.TryGetValue(userId, out var userClients))
            {
                userClients.RemoveAll(c => c.Id == clientId);
                
                // 해당 사용자의 클라이언트가 모두 제거되면 키 삭제
                if (userClients.Count == 0)
                {
                    _userClients.TryRemove(userId, out _);
                }
            }

            _logger.LogInformation("SSE client {ClientId} disconnected for user {UserId}", clientId, userId);
        }

        await Task.CompletedTask;
    }

    public async Task BroadcastToUserAsync(string userId, object eventData)
    {
        if (!_userClients.TryGetValue(userId, out var clients))
        {
            _logger.LogDebug("No SSE clients found for user {UserId}", userId);
            return;
        }

        var disconnectedClients = new List<SseClient>();

        foreach (var client in clients.ToList()) // ToList()로 복사본 생성
        {
            try
            {
                await SendEventToClientAsync(client, eventData);
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Failed to send event to client {ClientId}", client.Id);
                disconnectedClients.Add(client);
            }
        }

        // 연결이 끊어진 클라이언트들 제거
        foreach (var disconnectedClient in disconnectedClients)
        {
            await RemoveClientAsync(userId, disconnectedClient.Id);
        }

        _logger.LogDebug("Broadcasted event to {ClientCount} clients for user {UserId}", 
            clients.Count - disconnectedClients.Count, userId);
    }

    public async Task BroadcastToAllAsync(object eventData)
    {
        var disconnectedClients = new List<SseClient>();

        foreach (var client in _allClients.Values.ToList()) // ToList()로 복사본 생성
        {
            try
            {
                await SendEventToClientAsync(client, eventData);
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Failed to send event to client {ClientId}", client.Id);
                disconnectedClients.Add(client);
            }
        }

        // 연결이 끊어진 클라이언트들 제거
        foreach (var disconnectedClient in disconnectedClients)
        {
            await RemoveClientAsync(disconnectedClient.UserId, disconnectedClient.Id);
        }

        _logger.LogDebug("Broadcasted event to {ClientCount} clients", 
            _allClients.Count - disconnectedClients.Count);
    }

    public async Task SendHeartbeatAsync()
    {
        var heartbeatEvent = new
        {
            type = "heartbeat",
            timestamp = DateTimeOffset.UtcNow,
            serverId = "csharp-server",
            activeClients = _allClients.Count
        };

        await BroadcastToAllAsync(heartbeatEvent);
    }

    private async Task SendEventToClientAsync(SseClient client, object eventData)
    {
        if (client.Context.RequestAborted.IsCancellationRequested)
        {
            throw new OperationCanceledException("Client connection cancelled");
        }

        var jsonData = JsonSerializer.Serialize(eventData, new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        });

        var sseMessage = $"data: {jsonData}\n\n";
        var bytes = System.Text.Encoding.UTF8.GetBytes(sseMessage);

        await client.Context.Response.Body.WriteAsync(bytes);
        await client.Context.Response.Body.FlushAsync();
    }
}

public class SseClient
{
    public required string Id { get; set; }
    public required string UserId { get; set; }
    public required HttpContext Context { get; set; }
    public DateTimeOffset ConnectedAt { get; set; }
}