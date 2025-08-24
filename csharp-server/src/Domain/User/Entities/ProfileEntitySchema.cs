using Newtonsoft.Json;

namespace HandInHand.Domain.User.Entities
{
    public partial record ProfileEntity
    {
        [JsonProperty("nickname")]
        public string Nickname { get; init; } = "";

        [JsonProperty("level")]
        public int Level { get; init; } = 1;

        [JsonProperty("exp")]
        public int Exp { get; init; } = 0;

        [JsonProperty("avatar")]
        public string Avatar { get; init; } = "default";

        [JsonProperty("createdAt")]
        public string CreatedAt { get; init; } = "";

        [JsonProperty("updatedAt")]
        public string UpdatedAt { get; init; } = "";
    }
}