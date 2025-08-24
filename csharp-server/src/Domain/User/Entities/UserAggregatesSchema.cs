using System.Collections.Generic;
using Newtonsoft.Json;

namespace HandInHand.Domain.User.Entities
{
    public partial record UserAggregatesSchema
    {
        [JsonProperty("inventory")]
        public InventoryEntity Inventory { get; init; } = new InventoryEntity();

        [JsonProperty("profile")]
        public ProfileEntity Profile { get; init; } = new ProfileEntity();

        public static UserAggregatesSchema FromJson(string json) => JsonConvert.DeserializeObject<UserAggregatesSchema>(json)!;
    }

    public static class Serialize
    {
        public static string ToJson(this UserAggregatesSchema self) => JsonConvert.SerializeObject(self);
    }

    public static class Converter
    {
        public static UserAggregatesSchema FromJson(string json) => JsonConvert.DeserializeObject<UserAggregatesSchema>(json);
    }
}