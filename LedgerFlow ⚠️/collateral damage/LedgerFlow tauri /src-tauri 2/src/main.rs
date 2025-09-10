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
    invoice_id: String,
    date: String,
    customer_name: String,
    items: Vec<InvoiceItem>,
    tax_breakdown: serde_json::Value,
    grand_total: f64,
}

#[derive(Debug, Serialize, Deserialize)]
struct InvoiceItem {
    sku: String,
    name: String,
    qty: i32,
    rate: f64,
    tax: f64,
    total: f64,
}

#[derive(Debug, Serialize, Deserialize)]
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
    // Convert the config and catalog to JSON strings
    let config_json = serde_json::to_string(&config)
        .map_err(|e| format!("Failed to serialize config: {}", e))?;
    
    let catalog_json = serde_json::to_string(&catalog)
        .map_err(|e| format!("Failed to serialize catalog: {}", e))?;
    
    // Create temporary files to store the JSON data
    let temp_dir = std::env::temp_dir();
    let config_path = temp_dir.join("ledgerflow_config.json");
    let catalog_path = temp_dir.join("ledgerflow_catalog.json");
    let output_path = temp_dir.join("ledgerflow_output.json");
    
    fs::write(&config_path, config_json)
        .map_err(|e| format!("Failed to write config file: {}", e))?;
    
    fs::write(&catalog_path, catalog_json)
        .map_err(|e| format!("Failed to write catalog file: {}", e))?;
    
    // Determine the path to the Python script
    let script_path = Path::new("../backend/src/engine.py");
    
    // Run the Python script with the JSON files as arguments
    let output = Command::new("python")
        .arg(script_path)
        .arg("--config")
        .arg(&config_path)
        .arg("--catalog")
        .arg(&catalog_path)
        .arg("--output")
        .arg(&output_path)
        .output()
        .map_err(|e| format!("Failed to execute Python script: {}", e))?;
    
    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("Python script failed: {}", stderr));
    }
    
    // Read the output JSON file
    let output_json = fs::read_to_string(&output_path)
        .map_err(|e| format!("Failed to read output file: {}", e))?;
    
    // Parse the output JSON
    let result: SimulationResult = serde_json::from_str(&output_json)
        .map_err(|e| format!("Failed to parse output JSON: {}", e))?;
    
    // Clean up temporary files
    let _ = fs::remove_file(&config_path);
    let _ = fs::remove_file(&catalog_path);
    let _ = fs::remove_file(&output_path);
    
    Ok(result)
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![run_simulation])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
} 