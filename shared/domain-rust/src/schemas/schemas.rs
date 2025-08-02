// Example code that deserializes and serializes the model.
// extern crate serde;
// #[macro_use]
// extern crate serde_derive;
// extern crate serde_json;
//
// use generated_module::schemas;
//
// fn main() {
//     let json = r#"{"answer": 42}"#;
//     let model: schemas = serde_json::from_str(&json).unwrap();
// }

use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize)]
pub struct Schemas {
    pub profile: Profile,
    pub inventory: Inventory,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct Inventory {
    pub items: Vec<Item>,
    pub gold: i64,
    pub gems: i64,
    pub capacity: i64,
}

impl Inventory {
    pub fn new(gold: i64, gems: i64, capacity: i64) -> Inventory {
        Inventory {
            items: Vec::new(),
            gold,
            gems,
            capacity,
        }
    }

    pub fn gold(&self) -> i64 {
        self.gold
    }

    pub fn set_gold(&mut self, gold: i64) {
        self.gold = gold;
    }

    pub fn gems(&self) -> i64 {
        self.gems
    }

    pub fn set_gems(&mut self, gems: i64) {
        self.gems = gems;
    }

    pub fn capacity(&self) -> i64 {
        self.capacity
    }

    pub fn set_capacity(&mut self, capacity: i64) {
        self.capacity = capacity;
    }
}

#[derive(Serialize, Deserialize, Clone)]
pub struct Item {
    pub id: String,
    pub quantity: i64,
    pub level: Option<i64>,
    pub rarity: Option<String>,
    pub properties: Option<Properties>,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct Properties {
    pub attack: i64,
    pub durability: i64,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct Profile {
    pub nickname: String,
    pub level: i64,
    pub exp: i64,
    pub avatar: String,
    pub created_at: String,
}

impl Profile {
    pub fn new(nickname: String, level: i64, exp: i64, avatar: String, created_at: String) -> Profile {
        Profile {
            nickname,
            level,
            exp,
            avatar,
            created_at,
        }
    }

    pub fn nickname(&self) -> String {
        self.nickname.clone()
    }

    pub fn set_nickname(&mut self, nickname: String) {
        self.nickname = nickname;
    }

    pub fn level(&self) -> i64 {
        self.level
    }

    pub fn set_level(&mut self, level: i64) {
        self.level = level;
    }

    pub fn exp(&self) -> i64 {
        self.exp
    }

    pub fn set_exp(&mut self, exp: i64) {
        self.exp = exp;
    }

    pub fn avatar(&self) -> String {
        self.avatar.clone()
    }

    pub fn set_avatar(&mut self, avatar: String) {
        self.avatar = avatar;
    }

    pub fn created_at(&self) -> String {
        self.created_at.clone()
    }

    pub fn set_created_at(&mut self, created_at: String) {
        self.created_at = created_at;
    }
}
