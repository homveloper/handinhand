use serde::{Deserialize, Serialize};
use std::collections::HashMap;

// Re-export the generated schemas with better names
pub use crate::schemas::schemas::{
    Schemas as UserAggregates,
    Profile as ProfileEntity, 
    Inventory as InventoryEntity,
    Item,
    Properties as ItemProperties
};

/// Extension trait for ProfileEntity to add business logic
pub trait ProfileEntityExt {
    /// AddExp adds experience points to the profile
    /// Returns true if level increased, false otherwise
    fn AddExp(&mut self, exp_to_add: u32) -> bool;
    
    /// CalculateRequiredExpForLevel calculates required experience for a specific level
    fn CalculateRequiredExpForLevel(&self, target_level: u32) -> u32;
    
    /// GetExpToNextLevel gets experience needed for next level
    fn GetExpToNextLevel(&self) -> u32;
    
    /// GetLevelProgressPercentage gets experience progress percentage for current level (0-100)
    fn GetLevelProgressPercentage(&self) -> f64;
    
    /// IsValid validates profile data
    fn IsValid(&self) -> bool;
}

impl ProfileEntityExt for ProfileEntity {
    fn AddExp(&mut self, exp_to_add: u32) -> bool {
        let old_level = self.level as u32;
        self.exp += exp_to_add as i64;
        
        // Level up logic: 100 * level^1.5 exp needed for next level
        let mut level_increased = false;
        while self.level < 100 {
            let required_exp_for_next_level = self.CalculateRequiredExpForLevel(self.level as u32 + 1);
            if (self.exp as u32) >= required_exp_for_next_level {
                self.level += 1;
                level_increased = true;
            } else {
                break;
            }
        }
        
        level_increased
    }

    fn CalculateRequiredExpForLevel(&self, target_level: u32) -> u32 {
        if target_level <= 1 {
            return 0;
        }
        
        // Exponential growth formula: 100 * (level - 1)^1.5
        (100.0 * ((target_level - 1) as f64).powf(1.5)) as u32
    }

    fn GetExpToNextLevel(&self) -> u32 {
        if self.level >= 100 {
            return 0; // Max level reached
        }
        
        let required_for_next = self.CalculateRequiredExpForLevel(self.level as u32 + 1);
        let current_exp = self.exp as u32;
        if current_exp >= required_for_next {
            0
        } else {
            required_for_next - current_exp
        }
    }

    fn GetLevelProgressPercentage(&self) -> f64 {
        if self.level >= 100 {
            return 100.0;
        }
        
        let current_level_exp = self.CalculateRequiredExpForLevel(self.level as u32);
        let next_level_exp = self.CalculateRequiredExpForLevel(self.level as u32 + 1);
        let exp_in_current_level = (self.exp as u32) - current_level_exp;
        let exp_needed_for_level = next_level_exp - current_level_exp;
        
        if exp_needed_for_level == 0 {
            100.0
        } else {
            (exp_in_current_level as f64 / exp_needed_for_level as f64) * 100.0
        }
    }

    fn IsValid(&self) -> bool {
        !self.nickname.is_empty() 
            && self.nickname.len() <= 50
            && self.level >= 1 
            && self.level <= 100
            && !self.avatar.is_empty()
            && self.avatar.len() <= 100
    }
}

/// Extension trait for InventoryEntity to add business logic
pub trait InventoryEntityExt {
    /// AddGold adds gold to inventory
    fn AddGold(&mut self, amount: u32) -> bool;
    
    /// RemoveGold removes gold from inventory
    fn RemoveGold(&mut self, amount: u32) -> bool;
    
    /// AddGems adds gems to inventory
    fn AddGems(&mut self, amount: u32) -> bool;
    
    /// RemoveGems removes gems from inventory
    fn RemoveGems(&mut self, amount: u32) -> bool;
    
    /// GetItemCount gets current item count
    fn GetItemCount(&self) -> usize;
    
    /// HasSpace checks if inventory has space for more items
    fn HasSpace(&self) -> bool;
    
    /// IsValid validates inventory data
    fn IsValid(&self) -> bool;
}

impl InventoryEntityExt for InventoryEntity {
    fn AddGold(&mut self, amount: u32) -> bool {
        if self.gold.saturating_add(amount as i64) > 999_999_999 {
            return false;
        }
        self.gold += amount as i64;
        true
    }

    fn RemoveGold(&mut self, amount: u32) -> bool {
        if self.gold < amount as i64 {
            return false;
        }
        self.gold -= amount as i64;
        true
    }

    fn AddGems(&mut self, amount: u32) -> bool {
        if self.gems.saturating_add(amount as i64) > 999_999_999 {
            return false;
        }
        self.gems += amount as i64;
        true
    }

    fn RemoveGems(&mut self, amount: u32) -> bool {
        if self.gems < amount as i64 {
            return false;
        }
        self.gems -= amount as i64;
        true
    }

    fn GetItemCount(&self) -> usize {
        self.items.len()
    }

    fn HasSpace(&self) -> bool {
        self.items.len() < self.capacity as usize
    }

    fn IsValid(&self) -> bool {
        self.capacity >= 1 
            && self.capacity <= 1000
            && self.items.len() <= self.capacity as usize
            && self.gold <= 999_999_999
            && self.gems <= 999_999_999
    }
}

/// Extension trait for UserAggregates to add business logic
pub trait UserAggregatesExt {
    /// AddExpWithRewards adds experience to profile and potentially reward items/currency
    fn AddExpWithRewards(&mut self, exp_to_add: u32) -> bool;
    
    /// IsValid validates all user data
    fn IsValid(&self) -> bool;
}

impl UserAggregatesExt for UserAggregates {
    fn AddExpWithRewards(&mut self, exp_to_add: u32) -> bool {
        let old_level = self.profile.level as u32;
        let level_increased = self.profile.AddExp(exp_to_add);
        
        if level_increased {
            let new_level = self.profile.level as u32;
            let levels_gained = new_level - old_level;
            
            // Reward gold for leveling up: 100 * levels_gained * new_level
            let gold_reward = 100 * levels_gained * new_level;
            self.inventory.AddGold(gold_reward);
            
            // Reward gems every 5 levels
            if new_level % 5 == 0 {
                let gem_reward = new_level / 5;
                self.inventory.AddGems(gem_reward);
            }
        }
        
        level_increased
    }

    fn IsValid(&self) -> bool {
        self.profile.IsValid() && self.inventory.IsValid()
    }
}