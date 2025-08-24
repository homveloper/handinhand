using HandInHand.Domain.User.Entities;

namespace HandInHand.Server.Domain;

public static class Character
{
    public static (int newLevel, int newExp) AddExp(int currentExp, int expToAdd)
    {
        var totalExp = currentExp + expToAdd;
        var newLevel = totalExp / 1000 + 1;
        var remainingExp = totalExp % 1000;
        return (newLevel, remainingExp);
    }

    public static string? ValidateExp(int exp) =>
        exp <= 0 ? "Experience must be positive" :
        exp > 10000 ? "Too much experience at once" : null;

    public static ProfileEntity UpdateExp(ProfileEntity profile, int newLevel, int newExp) =>
        profile with 
        { 
            Level = newLevel, 
            Exp = newExp,
            UpdatedAt = DateTime.UtcNow.ToString("O")
        };

    public static string? ValidateNickname(string? nickname) =>
        string.IsNullOrWhiteSpace(nickname) ? "Nickname cannot be empty" :
        nickname.Length > 20 ? "Nickname too long" :
        nickname.Length < 2 ? "Nickname too short" : null;
}