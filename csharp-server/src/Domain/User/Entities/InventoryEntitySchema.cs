using System.Collections.Generic;
using Newtonsoft.Json;

namespace HandInHand.Domain.User.Entities
{
    public partial record InventoryEntity
    {
        [JsonProperty("capacity")]
        public long Capacity { get; init; } = 50;

        [JsonProperty("gems")]
        public long Gems { get; init; } = 0;

        [JsonProperty("gold")]
        public long Gold { get; init; } = 0;

        [JsonProperty("items")]
        public List<Item> Items { get; init; } = new List<Item>();
    }

    public partial record Item
    {
        [JsonProperty("id")]
        public string Id { get; init; } = "";

        [JsonProperty("level")]
        public long Level { get; init; } = 1;

        [JsonProperty("properties")]
        public Dictionary<string, object> Properties { get; init; } = new Dictionary<string, object>();

        [JsonProperty("quantity")]
        public long Quantity { get; init; } = 1;

        [JsonProperty("rarity")]
        public string Rarity { get; init; } = "common";
    }
}