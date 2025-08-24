namespace HandInHand.Server.Utils;

public static partial class ErrorHandling
{
    public static string? WrapRecover(Action action)
    {
        try
        {
            action();
            return null;
        }
        catch (Exception ex)
        {
            return ex.Message;
        }
    }

    public static (T? result, string? error) WrapRecover<T>(Func<T> func)
    {
        try
        {
            return (func(), null);
        }
        catch (Exception ex)
        {
            return (default, ex.Message);
        }
    }

    public static async Task<string?> WrapRecoverAsync(Func<Task> asyncAction)
    {
        try
        {
            await asyncAction();
            return null;
        }
        catch (Exception ex)
        {
            return ex.Message;
        }
    }

    public static async Task<(T? result, string? error)> WrapRecoverAsync<T>(Func<Task<T>> asyncFunc)
    {
        try
        {
            return (await asyncFunc(), null);
        }
        catch (Exception ex)
        {
            return (default, ex.Message);
        }
    }
}