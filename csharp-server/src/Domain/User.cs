using HandInHand.Domain.User.Entities;

namespace HandInHand.Server.Domain;

public static class User
{
    public static UserAggregatesSchema CreateNewUser(string userId, string? nickname)
    {
        var validationError = Character.ValidateNickname(nickname);
        if (validationError != null)
            throw new ArgumentException(validationError);

        return new UserAggregatesSchema
        {
            Profile = new ProfileEntity
            {
                Nickname = nickname ?? $"Player_{userId[..Math.Min(6, userId.Length)]}",
                Level = 1,
                Exp = 0,
                Avatar = "default",
                CreatedAt = DateTime.UtcNow.ToString("O"),
                UpdatedAt = DateTime.UtcNow.ToString("O")
            },
            Inventory = new InventoryEntity
            {
                Capacity = 50,
                Gold = 1000,
                Gems = 0,
                Items = new List<Item>()
            }
        };
    }

    public static UserAggregatesSchema AddUserExp(UserAggregatesSchema user, int exp)
    {
        var validationError = Character.ValidateExp(exp);
        if (validationError != null)
            throw new ArgumentException(validationError);

        var (newLevel, newExp) = Character.AddExp(user.Profile.Exp, exp);
        
        return user with
        {
            Profile = Character.UpdateExp(user.Profile, newLevel, newExp)
        };
    }

    public static UserAggregatesSchema AddGold(UserAggregatesSchema user, long gold)
    {
        if (gold <= 0)
            throw new ArgumentException("Gold amount must be positive");
        if (gold > 1000000)
            throw new ArgumentException("Gold amount too large");

        return user with
        {
            Inventory = user.Inventory with
            {
                Gold = user.Inventory.Gold + gold
            }
        };
    }

    public static UserAggregatesSchema UpdateNickname(UserAggregatesSchema user, string newNickname)
    {
        var validationError = Character.ValidateNickname(newNickname);
        if (validationError != null)
            throw new ArgumentException(validationError);

        return user with
        {
            Profile = user.Profile with
            {
                Nickname = newNickname,
                UpdatedAt = DateTime.UtcNow.ToString("O")
            }
        };
    }
}