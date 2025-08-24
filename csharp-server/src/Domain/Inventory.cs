using HandInHand.Domain.User.Entities;

namespace HandInHand.Server.Domain;

public static class Inventory
{
    public static string? ValidateGoldAmount(long gold) =>
        gold <= 0 ? "Gold amount must be positive" :
        gold > 1000000 ? "Gold amount too large" : null;

    public static string? ValidateItemQuantity(long quantity) =>
        quantity <= 0 ? "Item quantity must be positive" :
        quantity > 9999 ? "Item quantity too large" : null;

    public static InventoryEntity AddGold(InventoryEntity inventory, long gold)
    {
        var validationError = ValidateGoldAmount(gold);
        if (validationError != null)
            throw new ArgumentException(validationError);

        return inventory with { Gold = inventory.Gold + gold };
    }

    public static InventoryEntity AddItem(InventoryEntity inventory, string itemId, long quantity, string? rarity = null)
    {
        var quantityError = ValidateItemQuantity(quantity);
        if (quantityError != null)
            throw new ArgumentException(quantityError);

        if (inventory.Items.Count >= inventory.Capacity)
            throw new InvalidOperationException("Inventory is full");

        var existingItem = inventory.Items.FirstOrDefault(i => i.Id == itemId);
        
        if (existingItem != null)
        {
            var newItems = inventory.Items
                .Select(i => i.Id == itemId 
                    ? i with { Quantity = i.Quantity + quantity }
                    : i)
                .ToList();
            
            return inventory with { Items = newItems };
        }
        else
        {
            var newItem = new Item
            {
                Id = itemId,
                Quantity = quantity,
                Rarity = rarity ?? "common",
                Level = 1,
                Properties = new Dictionary<string, object>()
            };
            
            return inventory with { Items = inventory.Items.Append(newItem).ToList() };
        }
    }

    public static InventoryEntity RemoveItem(InventoryEntity inventory, string itemId, long quantity)
    {
        var quantityError = ValidateItemQuantity(quantity);
        if (quantityError != null)
            throw new ArgumentException(quantityError);

        var item = inventory.Items.FirstOrDefault(i => i.Id == itemId);
        if (item == null)
            throw new InvalidOperationException($"Item not found: {itemId}");

        if (item.Quantity > quantity)
        {
            var newItems = inventory.Items
                .Select(i => i.Id == itemId 
                    ? i with { Quantity = i.Quantity - quantity }
                    : i)
                .ToList();
            
            return inventory with { Items = newItems };
        }
        else
        {
            var newItems = inventory.Items
                .Where(i => i.Id != itemId)
                .ToList();
            
            return inventory with { Items = newItems };
        }
    }
}