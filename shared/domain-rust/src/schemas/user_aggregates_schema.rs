// Example code that deserializes and serializes the model.
// extern crate serde;
// #[macro_use]
// extern crate serde_derive;
// extern crate serde_json;
//
// use generated_module::user_aggregates_schema;
//
// fn main() {
//     let json = r#"{"answer": 42}"#;
//     let model: user_aggregates_schema = serde_json::from_str(&json).unwrap();
// }

use serde::{Serialize, Deserialize};
use std::collections::HashMap;

/// Complete user data aggregates containing all game content
#[derive(Serialize, Deserialize)]
pub struct UserAggregatesSchema {
    /// User inventory information
    inventory: InventoryEntity,

    /// User profile information
    profile: ProfileEntity,
}

/// User inventory information
///
/// User inventory information entity
#[derive(Serialize, Deserialize)]
pub struct InventoryEntity {
    /// Maximum inventory capacity
    capacity: i64,

    /// Gem amount
    gems: i64,

    /// Gold amount
    gold: i64,

    /// List of items in inventory
    items: Vec<Item>,
}

#[derive(Serialize, Deserialize)]
pub struct Item {
    /// Item identifier
    id: String,

    /// Item level (optional)
    level: Option<i64>,

    /// Additional item properties
    properties: Option<HashMap<String, Option<serde_json::Value>>>,

    /// Item quantity
    quantity: i64,

    /// Item rarity (optional)
    rarity: Option<Rarity>,
}

/// Item rarity (optional)
#[derive(Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Rarity {
    Common,

    Epic,

    Legendary,

    Rare,

    Uncommon,
}

/// User profile information
///
/// User profile information entity
#[derive(Serialize, Deserialize)]
pub struct ProfileEntity {
    /// Avatar identifier
    avatar: String,

    /// Account creation timestamp
    created_at: String,

    /// Experience points
    exp: i64,

    /// User level
    level: i64,

    /// User nickname
    nickname: String,
}
