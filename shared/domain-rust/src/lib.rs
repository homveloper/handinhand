use serde_json;
use std::ffi::{CStr, CString};
use std::os::raw::c_char;

// Module declarations
pub mod schemas;
pub mod types;

// Re-exports for easier access
pub use types::*;
pub use schemas::schemas::*;

/// Add adds two numbers (WASM export for WASI)
#[no_mangle]
pub extern "C" fn add(a: f64, b: f64) -> f64 {
    a + b
}

/// AddExpToProfileJson adds experience points to ProfileEntity (WASI compatible)
/// Takes JSON string and returns JSON string
#[no_mangle]
pub extern "C" fn add_exp_to_profile_json(profile_json_ptr: *const c_char, exp_to_add: u32) -> *mut c_char {
    let profile_json = unsafe {
        let cstr = CStr::from_ptr(profile_json_ptr);
        match cstr.to_str() {
            Ok(s) => s,
            Err(_) => return create_error_response("Invalid UTF-8 in profile JSON"),
        }
    };
    
    // Parse JSON to ProfileEntity
    let mut profile: ProfileEntity = match serde_json::from_str(profile_json) {
        Ok(p) => p,
        Err(e) => {
            let error_msg = format!("Failed to parse profile JSON: {}", e);
            return create_error_response(&error_msg);
        }
    };
    
    // Apply business logic
    let level_increased = profile.AddExp(exp_to_add);
    let exp_to_next = profile.GetExpToNextLevel();
    let progress = profile.GetLevelProgressPercentage();
    
    // Return JSON result
    let result = serde_json::json!({
        "profile": {
            "nickname": profile.nickname,
            "level": profile.level,
            "exp": profile.exp,
            "avatar": profile.avatar,
            "created_at": profile.created_at
        },
        "level_increased": level_increased,
        "exp_to_next_level": exp_to_next,
        "level_progress_percentage": progress
    });
    
    let result_string = result.to_string();
    match CString::new(result_string) {
        Ok(cstring) => cstring.into_raw(),
        Err(_) => create_error_response("Failed to create result string"),
    }
}

/// CalculateRequiredExp calculates required experience for a specific level (WASI compatible)
#[no_mangle]
pub extern "C" fn calculate_required_exp(target_level: u32) -> u32 {
    if target_level <= 1 {
        return 0;
    }
    
    // Exponential growth formula: 100 * (level - 1)^1.5
    (100.0 * ((target_level - 1) as f64).powf(1.5)) as u32
}

/// Free memory allocated by Rust (for strings returned to host)
#[no_mangle]
pub extern "C" fn free_string(ptr: *mut c_char) {
    if !ptr.is_null() {
        unsafe {
            let _ = CString::from_raw(ptr);
        }
    }
}

/// Helper function to create error response
fn create_error_response(error_msg: &str) -> *mut c_char {
    let error_result = serde_json::json!({
        "error": error_msg
    });
    
    let error_string = error_result.to_string();
    match CString::new(error_string) {
        Ok(cstring) => cstring.into_raw(),
        Err(_) => std::ptr::null_mut(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add() {
        assert_eq!(add(2.0, 3.0), 5.0);
        assert_eq!(add(-1.0, 1.0), 0.0);
        assert_eq!(add(0.0, 0.0), 0.0);
        assert_eq!(add(5.5, 4.5), 10.0);
    }

    #[test]
    fn test_calculate_required_exp() {
        assert_eq!(calculate_required_exp(1), 0);
        assert_eq!(calculate_required_exp(2), 100);
        assert_eq!(calculate_required_exp(3), 282); // 100 * 2^1.5 ≈ 282
        assert_eq!(calculate_required_exp(4), 519); // 100 * 3^1.5 ≈ 519
        assert_eq!(calculate_required_exp(10), 2700); // 100 * 9^1.5 = 2700
    }

    #[test]
    fn test_profile_add_exp_core() {
        use crate::types::ProfileEntityExt;
        
        let mut profile = ProfileEntity {
            nickname: "TestPlayer".to_string(),
            level: 1,
            exp: 0,
            avatar: "test_avatar".to_string(),
            created_at: "2024-01-01T00:00:00Z".to_string(),
        };
        
        let level_increased = profile.AddExp(500);
        
        assert_eq!(level_increased, true);
        assert_eq!(profile.level, 3); // 500 exp: level 1->3 (needs 0->100->282)
        assert_eq!(profile.exp, 500);
        
        let exp_to_next = profile.GetExpToNextLevel();
        let progress = profile.GetLevelProgressPercentage();
        
        assert!(exp_to_next > 0);
        assert!(progress >= 0.0 && progress <= 100.0);
    }
}