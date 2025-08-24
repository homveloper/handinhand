using HandInHand.Server.Api.Middleware;
using HandInHand.Server.Infrastructure;
using HandInHand.Domain.User.Entities;
using Serilog;
using StackExchange.Redis;
using HandInHand.Config;
using Microsoft.OpenApi.Models;

var builder = WebApplication.CreateBuilder(args);

// Serilog 설정
Log.Logger = new LoggerConfiguration()
    .ReadFrom.Configuration(builder.Configuration)
    .Enrich.FromLogContext()
    .WriteTo.Console()
    .CreateLogger();

builder.Host.UseSerilog();

// 설정 로드
var serverConfig = LoadServerConfig();
builder.Services.AddSingleton(serverConfig);

// Redis 연결 설정
builder.Services.AddSingleton<IDatabase>(provider =>
{
    var config = provider.GetRequiredService<ServerConfigSchema>();
    var connectionString = $"{config.Redis.Host}:{config.Redis.Port}";
    var redis = ConnectionMultiplexer.Connect(connectionString);
    return redis.GetDatabase();
});

// === 함수형 영속성 함수들 등록 ===
builder.Services.AddScoped<FindOneAndUpsertFunc<UserAggregatesSchema>>(provider =>
{
    var db = provider.GetRequiredService<IDatabase>();
    var logger = provider.GetRequiredService<ILogger<Program>>();

    // 기본 Redis Upsert + 재시도 + 로깅
    var baseUpsert = Persistence.CreateRedisUpsert<UserAggregatesSchema>(db, "user");
    var withRetry = Persistence.WithRetry(baseUpsert, maxRetries: 3);
    return Persistence.WithLogging(withRetry, logger);
});

builder.Services.AddScoped<FindOneAndUpdateFunc<UserAggregatesSchema>>(provider =>
{
    var db = provider.GetRequiredService<IDatabase>();
    var logger = provider.GetRequiredService<ILogger<Program>>();

    var baseUpdate = Persistence.CreateRedisUpdate<UserAggregatesSchema>(db, "user");
    return Persistence.WithLogging(baseUpdate, logger);
});

builder.Services.AddScoped<FindOneFunc<UserAggregatesSchema>>(provider =>
{
    var db = provider.GetRequiredService<IDatabase>();
    return Persistence.CreateRedisFind<UserAggregatesSchema>(db, "user");
});

// CORS 설정
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();

// 🚀 Swagger/SwaggerUI 설정
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "Hand in Hand Game Server API",
        Version = "v2.0",
        Description = "C# ASP.NET Core 기반 함수형 게임 서버 API<br/>" +
                     "<strong>완전 함수형 + IoC 아키텍처</strong><br/>" +
                     "도메인 함수 + 영속성 함수를 컨트롤러에서 조합하는 새로운 설계",
        Contact = new OpenApiContact
        {
            Name = "Game Server Team",
            Email = "dev@handinhand.game"
        },
        License = new OpenApiLicense
        {
            Name = "MIT License",
            Url = new Uri("https://opensource.org/licenses/MIT")
        }
    });

    // XML 문서 주석 활성화
    var xmlFile = $"{System.Reflection.Assembly.GetExecutingAssembly().GetName().Name}.xml";
    var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
    if (File.Exists(xmlPath))
    {
        c.IncludeXmlComments(xmlPath);
    }

    c.EnableAnnotations();
});

var app = builder.Build();

// Swagger 설정 (모든 환경에서 활성화)
app.UseSwagger();
app.UseSwaggerUI(c =>
{
    c.SwaggerEndpoint("/swagger/v1/swagger.json", "Hand in Hand Game Server API v2.0");
    c.RoutePrefix = "swagger";
    c.DefaultModelsExpandDepth(2);
    c.DefaultModelExpandDepth(2);
    c.DocExpansion(Swashbuckle.AspNetCore.SwaggerUI.DocExpansion.None);
    c.EnableDeepLinking();
    c.EnableFilter();
    
    // 커스텀 CSS 적용
    c.InjectStylesheet("/swagger/custom.css");
    
    // 커스텀 제목 설정
    c.DocumentTitle = "🚀 Hand in Hand Functional Game Server API";
});

app.UseCors();
app.UseMiddleware<GlobalExceptionHandlingMiddleware>();

// 컨트롤러 등록
app.MapControllers();

// 정적 파일 제공 (Swagger 커스텀 CSS용)
app.UseStaticFiles();

// Swagger UI 리다이렉트
app.MapGet("/", () => Results.Redirect("/swagger"));
app.MapGet("/docs", () => Results.Redirect("/swagger"));

// 서버 실행
var port = serverConfig.Servers.Csharp.Port;
Log.Information("🚀 Starting Functional C# server on port {Port}", port);
Log.Information("📖 Swagger UI: http://localhost:{Port}/swagger", port);
Log.Information("🏗️ Architecture: Functional Programming + IoC Pattern");

app.Run($"http://0.0.0.0:{port}");

// 설정 로드 함수
ServerConfigSchema LoadServerConfig()
{
    var configPath = Path.Combine(Directory.GetCurrentDirectory(), "..", "shared", "config", "server-config.json");
    if (!File.Exists(configPath))
    {
        throw new FileNotFoundException($"Server config not found at: {configPath}");
    }
    
    var configJson = File.ReadAllText(configPath);
    var config = ServerConfigSchema.FromJson(configJson);
    
    Log.Information("Server configuration loaded from {ConfigPath}", configPath);
    return config;
}