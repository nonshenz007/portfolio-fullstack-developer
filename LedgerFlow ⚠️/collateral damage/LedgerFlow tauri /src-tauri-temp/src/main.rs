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