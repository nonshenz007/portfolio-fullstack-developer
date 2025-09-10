// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::process::Command;
use std::path::Path;
use std::fs;

#[derive(Debug, Serialize, Deserialize)]
struct SimulationConfig {
    revenue_target: f64,
    start_date: String,
    end_date: String,
    invoice_type: String,
    min_items: i32,
    max_items: i32,
    min_invoice_amount: f64,
    max_invoice_amount: f64,
    item_filter_mode: String,
    selected_items: Vec<String>,
    name_type: String,
    realism_mode: String,
    seed: Option<i32>,
    invoice_count_mode: Option<String>,
    manual_invoice_count: Option<i32>,
    reality_buffer: Option<f64>,         // Added for reality buffer
    distribution_mode: Option<String>,   // Added for invoice distribution
    customer_repeat_rate: Option<f64>,   // Added for customer repeat rate
}

#[derive(Debug, Serialize, Deserialize)]
struct SimulationResult {
    invoices: Vec<Invoice>,
    status: String,
    error: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
struct Invoice {
    #[serde(rename = "invoice_type")]
    invoice_type: String,
    #[serde(rename = "invoice_number")]
    invoice_number: String,
    date: String,
    customer: serde_json::Value,
    items: Vec<InvoiceItem>,
    #[serde(rename = "subtotal")]
    subtotal: f64,
    #[serde(rename = "total")]
    total: f64,
    // Optional fields
    #[serde(skip_serializing_if = "Option::is_none")]
    payment_terms: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    template_applied: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
struct InvoiceItem {
    // Handle both "name" and "item" fields
    #[serde(rename = "name")]
    #[serde(default)]
    name: String,
    #[serde(rename = "item")]
    #[serde(default)]
    item: String,
    // Handle both "quantity" and "qty" fields
    #[serde(rename = "quantity")]
    #[serde(default)]
    quantity: i32,
    #[serde(rename = "qty")]
    #[serde(default)]
    qty: i32,
    #[serde(rename = "rate")]
    rate: f64,
    #[serde(rename = "amount")]
    amount: f64,
    // Optional fields for backward compatibility
    #[serde(skip_serializing_if = "Option::is_none")]
    sku: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    tax: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    total: Option<f64>,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct CatalogItem {
    sku: String,
    name: String,
    price: f64,
    gst_percent: Option<f64>,
    vat_percent: Option<f64>,
    category: Option<String>,
}

#[tauri::command]
async fn run_simulation(config: SimulationConfig, catalog: Vec<CatalogItem>) -> Result<SimulationResult, String> {
    println!("[Rust] Starting simulation with config: {:?}", config);
    
    // Validate required fields
    if config.revenue_target <= 0.0 {
        return Err("Revenue target must be positive".into());
    }
    if config.min_invoice_amount <= 0.0 || config.max_invoice_amount <= 0.0 {
        return Err("Invoice amounts must be positive".into());
    }
    if config.min_items <= 0 || config.max_items <= 0 {
        return Err("Item counts must be positive".into());
    }
    if config.min_invoice_amount > config.max_invoice_amount {
        return Err("Minimum invoice amount cannot exceed maximum".into());
    }
    if config.min_items > config.max_items {
        return Err("Minimum items cannot exceed maximum".into());
    }

    println!("[Rust] Serializing config...");
    let config_json = serde_json::to_string(&config)
        .map_err(|e| {
            println!("[Rust] Config serialization failed: {}", e);
            format!("Failed to serialize config: {}", e)
        })?;
    
    println!("[Rust] Serializing catalog...");
    let catalog_json = serde_json::to_string(&catalog)
        .map_err(|e| {
            println!("[Rust] Catalog serialization failed: {}", e);
            format!("Failed to serialize catalog: {}", e)
        })?;

    let script_path = Path::new("../backend/src/engine.py");
    println!("[Rust] Checking Python script at: {:?}", script_path);
    
    if !script_path.exists() {
        println!("[Rust] Python script not found!");
        return Err(format!("Python engine not found at: {:?}", script_path));
    }

    println!("[Rust] Executing Python engine...");
    let output = Command::new("python3")
        .arg(script_path)
        .arg("--config_json")
        .arg(&config_json)
        .arg("--catalog_json")
        .arg(&catalog_json)
        .output()
        .map_err(|e| {
            println!("[Rust] Python execution failed: {}", e);
            format!("Failed to execute Python engine: {}", e)
        })?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        println!("[Rust] Python engine error: {}", stderr);
        return Err(format!("Python engine error: {}", stderr));
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    println!("[Rust] Raw Python output: {}", stdout);
    
    let result: SimulationResult = serde_json::from_str(&stdout)
        .map_err(|e| {
            println!("[Rust] Failed to parse output: {}", e);
            format!("Failed to parse engine output: {}. Raw: {}", e, stdout)
        })?;

    if let Some(err) = result.error {
        println!("[Rust] Simulation returned error: {}", err);
        return Err(err);
    }

    println!("[Rust] Simulation completed successfully");
    Ok(result)
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![run_simulation])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
} 