using Microsoft.OpenApi.Models;
using Swashbuckle.AspNetCore.SwaggerGen;
using HandInHand.Server.Api.Models;

namespace HandInHand.Server.Api.Swagger;

/// <summary>
/// JSON-RPC 요청/응답 모델을 Swagger에서 더 명확하게 표시하기 위한 스키마 필터
/// </summary>
public class JsonRpcSchemaFilter : ISchemaFilter
{
    public void Apply(OpenApiSchema schema, SchemaFilterContext context)
    {
        if (context.Type.IsGenericType)
        {
            var genericType = context.Type.GetGenericTypeDefinition();
            
            // JSON-RPC 요청 모델 처리
            if (genericType == typeof(JsonRpcRequest<>))
            {
                var paramType = context.Type.GetGenericArguments()[0];
                
                schema.Description = $"JSON-RPC 2.0 요청 형식 (파라미터: {paramType.Name})";
                schema.Example = GenerateJsonRpcRequestExample(paramType);
                
                // 필수 필드 표시
                if (schema.Properties != null)
                {
                    if (schema.Properties.ContainsKey("jsonrpc"))
                    {
                        schema.Properties["jsonrpc"].Description = "JSON-RPC 버전 (항상 '2.0')";
                        schema.Properties["jsonrpc"].Example = new Microsoft.OpenApi.Any.OpenApiString("2.0");
                    }
                    
                    if (schema.Properties.ContainsKey("params"))
                    {
                        schema.Properties["params"].Description = $"요청 파라미터 ({paramType.Name})";
                    }
                    
                    if (schema.Properties.ContainsKey("id"))
                    {
                        schema.Properties["id"].Description = "요청 식별자 (선택사항)";
                        schema.Properties["id"].Example = new Microsoft.OpenApi.Any.OpenApiInteger(1);
                    }
                }
            }
            
            // JSON-RPC 응답 모델 처리
            else if (genericType == typeof(JsonRpcResponse<>))
            {
                var resultType = context.Type.GetGenericArguments()[0];
                
                schema.Description = $"JSON-RPC 2.0 응답 형식 (결과: {resultType.Name})";
                
                if (schema.Properties != null)
                {
                    if (schema.Properties.ContainsKey("jsonrpc"))
                    {
                        schema.Properties["jsonrpc"].Description = "JSON-RPC 버전 (항상 '2.0')";
                        schema.Properties["jsonrpc"].Example = new Microsoft.OpenApi.Any.OpenApiString("2.0");
                    }
                    
                    if (schema.Properties.ContainsKey("result"))
                    {
                        schema.Properties["result"].Description = $"성공시 결과 데이터 ({resultType.Name})";
                    }
                    
                    if (schema.Properties.ContainsKey("error"))
                    {
                        schema.Properties["error"].Description = "실패시 에러 정보";
                    }
                    
                    if (schema.Properties.ContainsKey("id"))
                    {
                        schema.Properties["id"].Description = "요청 식별자 (요청의 id와 동일)";
                    }
                }
            }
        }
        
        // 특정 파라미터 모델들에 대한 설명 추가
        else if (context.Type.Name.EndsWith("Params"))
        {
            schema.Description = $"{context.Type.Name} - JSON-RPC 파라미터 객체";
        }
    }
    
    private Microsoft.OpenApi.Any.IOpenApiAny? GenerateJsonRpcRequestExample(Type paramType)
    {
        // 파라미터 타입에 따른 예시 생성
        object exampleParams;
        switch (paramType.Name)
        {
            case "GetUserParams":
                exampleParams = new { userId = "user123" };
                break;
            case "CreateUserParams":
                exampleParams = new { userId = "user123", nickname = "플레이어123" };
                break;
            case "AddUserExpParams":
                exampleParams = new { userId = "user123", exp = 1000 };
                break;
            case "AddUserGoldParams":
                exampleParams = new { userId = "user123", gold = 5000 };
                break;
            case "UpdateUserNicknameParams":
                exampleParams = new { userId = "user123", nickname = "새닉네임" };
                break;
            default:
                exampleParams = new { };
                break;
        }
        
        var example = new
        {
            jsonrpc = "2.0",
            @params = exampleParams,
            id = 1
        };
        
        return new Microsoft.OpenApi.Any.OpenApiString(
            System.Text.Json.JsonSerializer.Serialize(example));
    }
}