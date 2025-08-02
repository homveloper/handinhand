// Example code that deserializes and serializes the model.
// extern crate serde;
// #[macro_use]
// extern crate serde_derive;
// extern crate serde_json;
//
// use generated_module::inventory_entity_schema;
//
// fn main() {
//     let json = r#"{"answer": 42}"#;
//     let model: inventory_entity_schema = serde_json::from_str(&json).unwrap();
// }

use serde::{Serialize, Deserialize};
use std::collections::HashMap;

/// User inventory information entity
#[derive(Serialize, Deserialize)]
pub struct InventoryEntitySchema {
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
