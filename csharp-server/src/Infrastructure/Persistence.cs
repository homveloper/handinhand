using StackExchange.Redis;
using System.Text.Json;
using System.Collections.Concurrent;
using Microsoft.Extensions.Caching.Memory;
using static HandInHand.Server.Utils.ErrorHandling;

namespace HandInHand.Server.Infrastructure;

// === 함수 타입 정의 ===
public delegate T CreateEntityFunc<T>(string id);
public delegate T UpdateEntityFunc<T>(T existing, string id); 
public delegate Task<(T? result, string? error)> FindOneAndUpsertFunc<T>(string id, CreateEntityFunc<T> createFn, UpdateEntityFunc<T> updateFn);
public delegate Task<(T? result, string? error)> FindOneAndUpdateFunc<T>(string id, UpdateEntityFunc<T> updateFn);
public delegate Task<(T? result, string? error)> FindOneFunc<T>(string id);
public delegate Task<string?> DeleteOneFunc(string id);

// 버전 관리용 인터페이스  
public interface IVersioned
{
    int Version { get; init; }
}

public static class Persistence
{
    // === Redis 기반 영속성 함수들 ===
    public static FindOneAndUpsertFunc<T> CreateRedisUpsert<T>(IDatabase db, string keyPrefix) =>
        async (id, createFn, updateFn) =>
            await WrapRecoverAsync(async () =>
            {
                var key = $"{keyPrefix}:{id}";
                var json = await db.StringGetAsync(key);

                T entity;
                if (!json.HasValue)
                {
                    entity = createFn(id);
                }
                else
                {
                    var existing = JsonSerializer.Deserialize<T>(json!)!;
                    entity = updateFn(existing, id);
                }

                var newJson = JsonSerializer.Serialize(entity);
                await db.StringSetAsync(key, newJson);

                return entity;
            });

    public static FindOneAndUpdateFunc<T> CreateRedisUpdate<T>(IDatabase db, string keyPrefix) =>
        async (id, updateFn) =>
            await WrapRecoverAsync(async () =>
            {
                var key = $"{keyPrefix}:{id}";
                var json = await db.StringGetAsync(key);

                if (!json.HasValue)
                    throw new InvalidOperationException($"Entity not found: {id}");

                var existing = JsonSerializer.Deserialize<T>(json!)!;
                var updated = updateFn(existing, id);

                var newJson = JsonSerializer.Serialize(updated);
                await db.StringSetAsync(key, newJson);

                return updated;
            });

    public static FindOneFunc<T> CreateRedisFind<T>(IDatabase db, string keyPrefix) =>
        async id =>
            await WrapRecoverAsync(async () =>
            {
                var key = $"{keyPrefix}:{id}";
                var json = await db.StringGetAsync(key);

                if (!json.HasValue)
                    throw new InvalidOperationException($"Entity not found: {id}");

                return JsonSerializer.Deserialize<T>(json!)!;
            });

    public static DeleteOneFunc CreateRedisDelete(IDatabase db, string keyPrefix) =>
        async id =>
        {
            var (result, error) = await WrapRecoverAsync(async () =>
            {
                var key = $"{keyPrefix}:{id}";
                var deleted = await db.KeyDeleteAsync(key);
                
                if (!deleted)
                    throw new InvalidOperationException($"Entity not found: {id}");
                    
                return "success";
            });
            return error;
        };

    // === 낙관적 동시성 제어 버전 ===
    public static FindOneAndUpsertFunc<T> CreateRedisUpsertWithVersion<T>(IDatabase db, string keyPrefix) 
        where T : IVersioned =>
        async (id, createFn, updateFn) =>
            await WrapRecoverAsync(async () =>
            {
                var key = $"{keyPrefix}:{id}";
                const int maxRetries = 5;

                for (int attempt = 0; attempt < maxRetries; attempt++)
                {
                    var json = await db.StringGetAsync(key);
                    T entity;

                    if (!json.HasValue)
                    {
                        entity = createFn(id);
                        // 버전 설정은 entity 생성 시 처리
                    }
                    else
                    {
                        var existing = JsonSerializer.Deserialize<T>(json!)!;
                        entity = updateFn(existing, id);
                        // 버전 업데이트는 updateFn에서 처리
                    }

                    var newJson = JsonSerializer.Serialize(entity);
                    
                    // 낙관적 락 시뮬레이션 (실제 Redis Lua 스크립트 사용 권장)
                    var currentJson = await db.StringGetAsync(key);
                    if (json.Equals(currentJson)) // 변경되지 않았으면
                    {
                        await db.StringSetAsync(key, newJson);
                        return entity;
                    }

                    await Task.Delay(Random.Shared.Next(10, 50));
                }

                throw new InvalidOperationException("Too many concurrent updates, please retry");
            });

    // === 메모리 구현체 (테스트용) ===
    public static FindOneAndUpsertFunc<T> CreateMemoryUpsert<T>(ConcurrentDictionary<string, T> storage) =>
        async (id, createFn, updateFn) =>
        {
            await Task.CompletedTask;
            var result = storage.AddOrUpdate(id, 
                _ => createFn(id),           
                (_, existing) => updateFn(existing, id)); 

            return (result, null);
        };

    public static FindOneAndUpdateFunc<T> CreateMemoryUpdate<T>(ConcurrentDictionary<string, T> storage) =>
        async (id, updateFn) =>
        {
            await Task.CompletedTask;
            if (!storage.TryGetValue(id, out var existing))
                return (default, $"Entity not found: {id}");
                
            var updated = updateFn(existing, id);
            storage.TryUpdate(id, updated, existing);
            
            return (updated, null);
        };

    public static FindOneFunc<T> CreateMemoryFind<T>(ConcurrentDictionary<string, T> storage) =>
        async id =>
        {
            await Task.CompletedTask;
            return storage.TryGetValue(id, out var entity) 
                ? (entity, null) 
                : (default, $"Entity not found: {id}");
        };

    // === 조합 함수들 (Decorators) ===
    public static FindOneAndUpsertFunc<T> WithRetry<T>(FindOneAndUpsertFunc<T> upsert, int maxRetries = 3) =>
        async (id, createFn, updateFn) =>
        {
            for (int i = 0; i < maxRetries; i++)
            {
                var (result, error) = await upsert(id, createFn, updateFn);
                
                if (error == null) return (result, error);
                if (i == maxRetries - 1) return (result, error);

                await Task.Delay(TimeSpan.FromMilliseconds(100 * Math.Pow(2, i)));
            }
            
            return (default, "Max retries exceeded");
        };

    public static FindOneAndUpsertFunc<T> WithLogging<T>(FindOneAndUpsertFunc<T> upsert, ILogger logger) =>
        async (id, createFn, updateFn) =>
        {
            logger.LogInformation("Starting upsert for entity: {EntityId}", id);
            var (result, error) = await upsert(id, createFn, updateFn);
            
            if (error != null)
                logger.LogError("Upsert failed for {EntityId}: {Error}", id, error);
            else
                logger.LogInformation("Upsert succeeded for {EntityId}", id);
                
            return (result, error);
        };

    public static FindOneAndUpdateFunc<T> WithLogging<T>(FindOneAndUpdateFunc<T> update, ILogger logger) =>
        async (id, updateFn) =>
        {
            logger.LogInformation("Starting update for entity: {EntityId}", id);
            var (result, error) = await update(id, updateFn);
            
            if (error != null)
                logger.LogError("Update failed for {EntityId}: {Error}", id, error);
            else
                logger.LogInformation("Update succeeded for {EntityId}", id);
                
            return (result, error);
        };

    public static FindOneFunc<T> WithCache<T>(FindOneFunc<T> finder, IMemoryCache cache, TimeSpan expiry) =>
        async id =>
        {
            var cacheKey = $"entity_cache_{typeof(T).Name}_{id}";
            if (cache.TryGetValue(cacheKey, out T cachedEntity))
                return (cachedEntity, null);

            var (entity, error) = await finder(id);
            if (entity != null && error == null)
                cache.Set(cacheKey, entity, expiry);
            
            return (entity, error);
        };
}