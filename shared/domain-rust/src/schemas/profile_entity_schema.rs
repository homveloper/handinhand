// Example code that deserializes and serializes the model.
// extern crate serde;
// #[macro_use]
// extern crate serde_derive;
// extern crate serde_json;
//
// use generated_module::profile_entity_schema;
//
// fn main() {
//     let json = r#"{"answer": 42}"#;
//     let model: profile_entity_schema = serde_json::from_str(&json).unwrap();
// }

use serde::{Serialize, Deserialize};

/// User profile information entity
#[derive(Serialize, Deserialize)]
pub struct ProfileEntitySchema {
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
