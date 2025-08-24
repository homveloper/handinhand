namespace HandInHand.Server.Api.Attributes;

/// <summary>
/// JSON-RPC 메서드 문서화를 위한 어트리뷰트
/// </summary>
[AttributeUsage(AttributeTargets.Method)]
public class JsonRpcMethodAttribute : Attribute
{
    public string Name { get; }
    public string Description { get; set; } = "";
    public string Summary { get; set; } = "";
    public string[] Tags { get; set; } = Array.Empty<string>();

    public JsonRpcMethodAttribute(string name)
    {
        Name = name;
    }
}

/// <summary>
/// JSON-RPC 파라미터 문서화를 위한 어트리뷰트
/// </summary>
[AttributeUsage(AttributeTargets.Parameter)]
public class JsonRpcParamAttribute : Attribute
{
    public string Name { get; }
    public string Description { get; set; } = "";
    public bool Required { get; set; } = true;
    public object? Example { get; set; }

    public JsonRpcParamAttribute(string name)
    {
        Name = name;
    }
}

/// <summary>
/// JSON-RPC 리턴값 문서화를 위한 어트리뷰트
/// </summary>
[AttributeUsage(AttributeTargets.Method)]
public class JsonRpcReturnAttribute : Attribute
{
    public string Description { get; set; } = "";
    public object? Example { get; set; }

    public JsonRpcReturnAttribute(string description = "")
    {
        Description = description;
    }
}

/// <summary>
/// JSON-RPC 에러 문서화를 위한 어트리뷰트
/// </summary>
[AttributeUsage(AttributeTargets.Method, AllowMultiple = true)]
public class JsonRpcErrorAttribute : Attribute
{
    public int Code { get; }
    public string Message { get; }
    public string Description { get; set; } = "";

    public JsonRpcErrorAttribute(int code, string message)
    {
        Code = code;
        Message = message;
    }
}