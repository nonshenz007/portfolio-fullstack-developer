#this file will contain the UI for the dashboard page. 

import flet as ft
from datetime import datetime, timedelta
from utils.invoice_generator import generate_plain_invoices

def get_template_color(template):
    """Get color scheme for different templates"""
    colors = {
        "Plain": "#10B981",   # Green
        "GST": "#F59E0B",     # Orange  
        "VAT": "#7C3AED"      # Purple
    }
    return colors.get(template, "#6B7280")

class SimulationState:
    """Manages the simulation state and validation"""
    def __init__(self):
        # Core states
        self.template_selected = False
        self.selected_template = None
        self.catalog_uploaded = False
        self.parameters_valid = False
        self.simulation_running = False
        self.simulation_complete = False
        self.verification_complete = False
        self.export_ready = False
        
        # Progress tracking
        self.current_progress = 0
        self.total_invoices = 0
        self.total_revenue = 0
        self.avg_amount = 0
        self.error_state = None
        self.verification_score = 0
        
        # Parameter validation
        self.revenue_target_valid = False
        self.date_range_valid = False
        self.invoice_limits_valid = False
        self.business_settings_valid = False
        
        # Verification checks
        self.revenue_match_verified = False
        self.tax_logic_verified = False
        self.format_verified = False
        
    def validate_parameters(self):
        """Check if all required parameters are valid"""
        self.parameters_valid = all([
            self.revenue_target_valid,
            self.date_range_valid,
            self.invoice_limits_valid,
            self.business_settings_valid
        ])
        return self.parameters_valid
        
    def can_start_simulation(self):
        """Check if simulation can be started"""
        return (self.template_selected and 
                self.parameters_valid and 
                not self.simulation_running)
    
    def can_export(self):
        """Check if export is allowed"""
        return (self.simulation_complete and 
                self.verification_complete and 
                self.verification_score >= 85)
    
    def reset_simulation(self):
        """Reset simulation state for new run"""
        self.simulation_running = False
        self.simulation_complete = False
        self.verification_complete = False
        self.export_ready = False
        self.current_progress = 0
        self.error_state = None
        
    def reset_template(self):
        """Reset everything for template reselection"""
        self.__init__()  # Full reset

    def update_verification_score(self):
        """Calculate verification score based on checks"""
        checks = [
            self.revenue_match_verified,
            self.tax_logic_verified,
            self.format_verified
        ]
        self.verification_score = (sum(1 for c in checks if c) / len(checks)) * 100
        self.verification_complete = self.verification_score >= 85
        return self.verification_score

def dashboard_view(page: ft.Page):
    # Initialize simulation state
    sim_state = SimulationState()
    
    # State variables
    selected_template = None
    uploaded_catalog = None
    generated_invoices = []
    verification_results = None
    
    # Form field refs
    revenue_target_ref = ft.Ref[ft.TextField]()
    start_date_ref = ft.Ref[ft.TextField]()
    end_date_ref = ft.Ref[ft.TextField]()
    business_style_ref = ft.Ref[ft.Dropdown]()
    realism_mode_ref = ft.Ref[ft.Dropdown]()
    max_invoices_ref = ft.Ref[ft.TextField]()
    min_amount_ref = ft.Ref[ft.TextField]()
    max_amount_ref = ft.Ref[ft.TextField]()
    price_rounding_ref = ft.Ref[ft.Dropdown]()
    customer_diversity_ref = ft.Ref[ft.Slider]()
    date_spread_ref = ft.Ref[ft.Slider]()
    tax_accuracy_ref = ft.Ref[ft.Dropdown]()
    test_mode_ref = ft.Ref[ft.Switch]()
    
    # Export settings refs
    tax_breakdown_ref = ft.Ref[ft.Switch]()
    audit_trail_ref = ft.Ref[ft.Switch]()
    save_config_ref = ft.Ref[ft.Switch]()

    def create_panel_card(title: str, content: ft.Control, width: int = None):
        """Creates a consistent panel card with title"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(title, size=16, weight="bold", color="#1F2937"),
                    ft.Container(height=16),
                    content
                ]),
                padding=20,
                width=width
            ),
            elevation=1
        )

    def create_template_selection_screen():
        """Initial template selection screen with animations"""
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Text("Choose Invoice Template", size=24, weight="bold", color="#1F2937"),
                        ft.Text("Select the type of invoice you want to generate", size=14, color="#6B7280"),
                    ], spacing=8),
                    padding=ft.padding.only(bottom=32),
                    animate_opacity=300,
                    opacity=1
                ),
                
                ft.Row([
                    # Plain Invoice Card
                    ft.Container(
                        content=ft.Column([
                            ft.Container(
                                content=ft.Icon("description", size=32, color="#10B981"),
                                padding=12,
                                bgcolor="#F0FDF4",
                                border_radius=8
                            ),
                            ft.Container(height=16),
                            ft.Text("Plain Invoice", size=18, weight="bold", color="#1F2937"),
                            ft.Container(height=8),
                            ft.Text(
                                "Simple, clean invoices without tax calculations", 
                                size=14, 
                                color="#6B7280",
                                text_align=ft.TextAlign.CENTER
                            ),
                            ft.Container(height=16),
                            ft.ElevatedButton(
                                "Select Plain",
                                color="white",
                                bgcolor="#10B981",
                                width=200,
                                on_click=lambda e: select_template("Plain"),
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8)
                                )
                            )
                        ], 
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4
                    ),
                    padding=32,
                    bgcolor="white",
                    border_radius=12,
                    border=ft.border.all(1, "#E5E7EB"),
                    animate_scale=300,
                    scale=1,
                    animate_opacity=300,
                    opacity=1,
                    on_hover=lambda e: handle_card_hover(e, "Plain"),
                    expand=True
                ),
                
                # GST Invoice Card
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Icon("receipt", size=32, color="#F59E0B"),
                            padding=12,
                            bgcolor="#FEF3C7",
                            border_radius=8
                        ),
                        ft.Container(height=16),
                        ft.Text("GST Invoice", size=18, weight="bold", color="#1F2937"),
                        ft.Container(height=8),
                        ft.Text(
                            "Indian GST-compliant invoices with tax calculations", 
                            size=14,
                            color="#6B7280",
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Container(height=16),
                        ft.ElevatedButton(
                            "Select GST",
                            color="white",
                            bgcolor="#F59E0B",
                            width=200,
                            on_click=lambda e: select_template("GST"),
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8)
                            )
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4
                ),
                padding=32,
                bgcolor="white",
                border_radius=12,
                border=ft.border.all(1, "#E5E7EB"),
                animate_scale=300,
                scale=1,
                animate_opacity=300,
                opacity=1,
                on_hover=lambda e: handle_card_hover(e, "GST"),
                expand=True
            ),
                
            # VAT Invoice Card
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Icon("account_balance", size=32, color="#7C3AED"),
                        padding=12,
                        bgcolor="#F3E8FF",
                        border_radius=8
                    ),
                    ft.Container(height=16),
                    ft.Text("VAT Invoice", size=18, weight="bold", color="#1F2937"),
                    ft.Container(height=8),
                    ft.Text(
                        "VAT-compliant invoices for international trade", 
                        size=14,
                        color="#6B7280",
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Container(height=16),
                    ft.ElevatedButton(
                        "Select VAT",
                        color="white",
                        bgcolor="#7C3AED",
                        width=200,
                        on_click=lambda e: select_template("VAT"),
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8)
                        )
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4
            ),
            padding=32,
            bgcolor="white",
            border_radius=12,
            border=ft.border.all(1, "#E5E7EB"),
            animate_scale=300,
            scale=1,
            animate_opacity=300,
            opacity=1,
            on_hover=lambda e: handle_card_hover(e, "VAT"),
            expand=True
        )], spacing=24, alignment=ft.MainAxisAlignment.CENTER)
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
    padding=64,
    alignment=ft.alignment.center,
    animate_opacity=300,
    opacity=1
)

    def handle_card_hover(e, template_type):
        """Handle hover animation for template cards"""
        if e.data == "true":  # Mouse enter
            e.control.scale = 1.02
            e.control.update()
        else:  # Mouse exit
            e.control.scale = 1
            e.control.update()

    def create_simulation_layout():
        """Creates the 3-column simulation layout with animations"""
        if not sim_state.template_selected:
            return create_template_selection_screen()
            
        return ft.Row([
            # Left Panel - Parameters (300px)
            ft.Container(
                content=create_parameters_panel(),
                width=300,
                animate_opacity=300,
                opacity=1
            ),
                
            # Center Panel - Monitor (dynamic)
            ft.Container(
                content=create_monitor_panel(),
                expand=True,
                animate_opacity=300,
                opacity=1
            ),
            
            # Right Panel - Export Control (280px)
            ft.Container(
                content=create_export_panel(),
                width=280,
                animate_opacity=300,
                opacity=1
            )
        ], spacing=24, expand=True)

    def create_parameters_panel():
        """Left panel with simulation parameters"""
        def validate_revenue(e):
            """Validate revenue target input"""
            try:
                value = float(revenue_target_ref.current.value.replace(",", ""))
                sim_state.revenue_target_valid = 1000 <= value <= 1000000
                revenue_target_ref.current.error_text = None if sim_state.revenue_target_valid else "Enter amount between ₹1,000 and ₹10,00,000"
            except ValueError:
                sim_state.revenue_target_valid = False
                revenue_target_ref.current.error_text = "Enter a valid amount"
            sim_state.validate_parameters()
            page.update()
            
        def validate_dates(e):
            """Validate date range inputs"""
            try:
                start = datetime.strptime(start_date_ref.current.value, "%Y-%m-%d")
                end = datetime.strptime(end_date_ref.current.value, "%Y-%m-%d")
                valid_range = 1 <= (end - start).days <= 90
                sim_state.date_range_valid = valid_range
                
                if not valid_range:
                    start_date_ref.current.error_text = "Date range should be between 1 and 90 days"
                    end_date_ref.current.error_text = "Date range should be between 1 and 90 days"
                else:
                    start_date_ref.current.error_text = None
                    end_date_ref.current.error_text = None
            except ValueError:
                sim_state.date_range_valid = False
                start_date_ref.current.error_text = "Enter valid date (YYYY-MM-DD)"
                end_date_ref.current.error_text = "Enter valid date (YYYY-MM-DD)"
            sim_state.validate_parameters()
            page.update()
            
        def validate_invoice_limits(e):
            """Validate invoice count and amount limits"""
            try:
                max_count = int(max_invoices_ref.current.value)
                min_amt = float(min_amount_ref.current.value.replace(",", ""))
                max_amt = float(max_amount_ref.current.value.replace(",", ""))
                
                count_valid = 1 <= max_count <= 100
                amounts_valid = 100 <= min_amt < max_amt <= 100000
                
                sim_state.invoice_limits_valid = count_valid and amounts_valid
                
                max_invoices_ref.current.error_text = None if count_valid else "Enter between 1 and 100"
                min_amount_ref.current.error_text = None if amounts_valid else "Min amount should be ≥ ₹100"
                max_amount_ref.current.error_text = None if amounts_valid else "Max amount should be ≤ ₹1,00,000"
                
            except ValueError:
                sim_state.invoice_limits_valid = False
                max_invoices_ref.current.error_text = "Enter a valid number"
                min_amount_ref.current.error_text = "Enter a valid amount"
                max_amount_ref.current.error_text = "Enter a valid amount"
            sim_state.validate_parameters()
            page.update()
            
        def validate_business_settings(e):
            """Validate business category and realism settings"""
            sim_state.business_settings_valid = (
                business_style_ref.current.value is not None and
                realism_mode_ref.current.value is not None
            )
            sim_state.validate_parameters()
            page.update()

        return ft.Container(
            content=ft.Column([
                # Template info
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Container(
                                content=ft.Icon(
                                    "description",
                                    size=20,
                                    color=get_template_color(sim_state.selected_template)
                                ),
                                padding=8,
                                bgcolor="#F9FAFB",
                                border_radius=4
                            ),
                            ft.Text(
                                f"{sim_state.selected_template} Invoice",
                                size=14,
                                weight="w500",
                                color="#1F2937"
                            )
                        ], spacing=8),
                        ft.Container(height=4),
                        ft.Text(
                            "Configure parameters below to generate invoices",
                            size=12,
                            color="#6B7280"
                        )
                    ]),
                    padding=16,
                    bgcolor="#FFFFFF",
                    border_radius=8,
                    border=ft.border.all(1, "#E5E7EB")
                ),
                
                ft.Container(height=24),
                
                # Catalog Upload Section
                ft.Container(
                    content=ft.Column([
                        ft.Text("Catalog Source", size=14, weight="w500"),
                        ft.ElevatedButton(
                            "Upload XLSX",
                            icon="upload",
                            on_click=lambda _: print("Upload"),
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8)
                            )
                        ),
                        ft.Text("or use default catalog", size=12, color="#6B7280")
                    ], spacing=8),
                    padding=16,
                    bgcolor="#F9FAFB",
                    border_radius=8
                ),
                
                ft.Divider(height=32, color="#E5E7EB"),
                
                # Basic Parameters
                ft.Text("Basic Parameters", size=14, weight="w500"),
                ft.Container(height=16),
                
                ft.TextField(
                    ref=revenue_target_ref,
                    label="Revenue Target",
                    prefix_text="₹",
                    value="50000",
                    on_change=validate_revenue,
                    border_radius=8
                ),
                
                ft.Container(height=16),
                
                ft.Text("Date Range", size=14, weight="w500"),
                ft.Row([
                    ft.TextField(
                        ref=start_date_ref,
                        label="From",
                        value="2024-01-01",
                        width=130,
                        on_change=validate_dates,
                        border_radius=8
                    ),
                    ft.TextField(
                        ref=end_date_ref,
                        label="To",
                        value="2024-01-31",
                        width=130,
                        on_change=validate_dates,
                        border_radius=8
                    )
                ], spacing=8),
                
                ft.Container(height=24),
                
                # Business Settings
                ft.Text("Business Settings", size=14, weight="w500"),
                ft.Dropdown(
                    ref=business_style_ref,
                    label="Category",
                    value="Medical & Pharmaceutical",
                    options=[
                        ft.dropdown.Option("Medical & Pharmaceutical"),
                        ft.dropdown.Option("Grocery & Food Items"),
                        ft.dropdown.Option("Clothing & Textiles")
                    ],
                    on_change=validate_business_settings,
                    border_radius=8
                ),
                
                ft.Container(height=8),
                
                ft.Dropdown(
                    ref=realism_mode_ref,
                    label="Realism",
                    value="Standard",
                    options=[
                        ft.dropdown.Option("Conservative"),
                        ft.dropdown.Option("Standard"),
                        ft.dropdown.Option("Aggressive")
                    ],
                    on_change=validate_business_settings,
                    border_radius=8
                ),
                
                ft.Container(height=24),
                
                # Invoice Controls
                ft.Text("Invoice Controls", size=14, weight="w500"),
                ft.TextField(
                    ref=max_invoices_ref,
                    label="Max Daily Invoices",
                    value="15",
                    on_change=validate_invoice_limits,
                    border_radius=8
                ),
                
                ft.Row([
                    ft.TextField(
                        ref=min_amount_ref,
                        label="Min Amount",
                        value="100",
                        width=130,
                        on_change=validate_invoice_limits,
                        border_radius=8
                    ),
                    ft.TextField(
                        ref=max_amount_ref,
                        label="Max Amount",
                        value="10000",
                        width=130,
                        on_change=validate_invoice_limits,
                        border_radius=8
                    )
                ], spacing=8),
                
                ft.Container(height=24),
                
                # Advanced Settings Header (clickable)
                ft.Container(
                    content=ft.Row([
                        ft.Text("Advanced Settings", size=14, weight="w500"),
                        ft.Container(width=8),
                        ft.IconButton(
                            icon="expand_more",
                            rotate=0,
                            on_click=toggle_advanced,
                            icon_size=20
                        )
                    ]),
                    on_click=toggle_advanced
                ),
                
                # Advanced Settings Content (expandable)
                advanced_content,
                
                ft.Container(height=16),
                
                ft.Switch(
                    ref=test_mode_ref,
                    label="Test Mode",
                    value=False
                )
            ], scroll=ft.ScrollMode.AUTO),
            width=300,
            bgcolor="white",
            border_radius=12,
            border=ft.border.all(1, "#E5E7EB"),
            padding=24,
            animate=ft.animation.Animation(500, "easeOut")
        )

    def create_monitor_panel():
        """Center panel showing simulation status and results"""
        if not sim_state.simulation_running and not sim_state.simulation_complete:
            return ft.Container(
                content=ft.Column([
                    # Back button
                    ft.Container(
                        content=ft.Row([
                            ft.IconButton(
                                icon="arrow_back",
                                on_click=lambda _: reset_template(),
                                icon_color="#6B7280"
                            ),
                            ft.Text("Back to Template Selection", 
                                  size=14, color="#6B7280")
                        ], spacing=8),
                        margin=ft.margin.only(bottom=24)
                    ),
                    
                    # Ready to start content
                    ft.Container(
                        content=ft.Column([
                            ft.Icon("play_circle", size=48, color="#6B7280"),
                            ft.Container(height=16),
                            ft.Text("Ready to Start", 
                                  size=20, weight="bold", color="#1F2937"),
                            ft.Text("Configure parameters and click Start Simulation", 
                                  size=14, color="#6B7280")
                        ], 
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8),
                        padding=48,
                        alignment=ft.alignment.center
                    ),
                    
                    ft.Container(height=32),
                    
                    # Start button
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon("play_arrow"),
                            ft.Text("Start Simulation", size=16)
                        ], spacing=8),
                        bgcolor="#1565C0" if sim_state.can_start_simulation() else "#E5E7EB",
                        color="white" if sim_state.can_start_simulation() else "#9CA3AF",
                        disabled=not sim_state.can_start_simulation(),
                        width=float('inf'),
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8)
                        ),
                        on_click=lambda _: start_simulation()
                    )
                ], 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER),
                padding=32,
                bgcolor="white",
                border_radius=12,
                border=ft.border.all(1, "#E5E7EB")
            )
            
        if sim_state.simulation_running:
            return ft.Container(
                content=ft.Column([
                    ft.ProgressBar(
                        value=sim_state.current_progress / 100,
                        bgcolor="#F3F4F6",
                        color="#1565C0",
                        height=8
                    ),
                    ft.Container(height=16),
                    ft.Text(
                        f"Generating Invoices... {sim_state.current_progress}%",
                        size=14, 
                        color="#6B7280",
                        weight="w500"
                    ),
                    ft.Container(height=24),
                    ft.Row([
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Invoices", size=12, color="#6B7280"),
                                ft.Text(str(sim_state.total_invoices), 
                                      size=24, weight="bold", color="#1F2937")
                            ], spacing=4),
                            padding=16,
                            bgcolor="#F9FAFB",
                            border_radius=8,
                            expand=True
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Revenue", size=12, color="#6B7280"),
                                ft.Text(f"₹{sim_state.total_revenue:,}", 
                                      size=24, weight="bold", color="#1F2937")
                            ], spacing=4),
                            padding=16,
                            bgcolor="#F9FAFB",
                            border_radius=8,
                            expand=True
                        )
                    ], spacing=16)
                ]),
                padding=32,
                bgcolor="white",
                border_radius=12,
                border=ft.border.all(1, "#E5E7EB"),
                animate=ft.animation.Animation(500, "easeOut")
            )
            
        # Show results if simulation is complete
        return ft.Container(
            content=ft.Column([
                # Success banner
                ft.Container(
                    content=ft.Row([
                        ft.Icon("check_circle", color="#10B981", size=24),
                        ft.Column([
                            ft.Text("Generation Complete!", 
                                  size=18, weight="bold", color="#065F46"),
                            ft.Text("Ready for verification", 
                                  size=14, color="#047857")
                        ])
                    ], spacing=12),
                    padding=16,
                    bgcolor="#ECFDF5",
                    border_radius=8
                ),
                
                ft.Container(height=24),
                
                # Stats cards
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Total Invoices", size=12, color="#6B7280"),
                            ft.Text(str(sim_state.total_invoices), 
                                  size=24, weight="bold", color="#1F2937")
                        ], spacing=4),
                        padding=16,
                        bgcolor="#F9FAFB",
                        border_radius=8,
                        expand=True
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Total Revenue", size=12, color="#6B7280"),
                            ft.Text(f"₹{sim_state.total_revenue:,}", 
                                  size=24, weight="bold", color="#1F2937")
                        ], spacing=4),
                        padding=16,
                        bgcolor="#F9FAFB",
                        border_radius=8,
                        expand=True
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Average Amount", size=12, color="#6B7280"),
                            ft.Text(f"₹{sim_state.avg_amount:,}", 
                                  size=24, weight="bold", color="#1F2937")
                        ], spacing=4),
                        padding=16,
                        bgcolor="#F9FAFB",
                        border_radius=8,
                        expand=True
                    )
                ], spacing=16),
                
                ft.Container(height=24),
                
                # Sample invoices
                ft.Text("Sample Invoices", size=14, weight="w500"),
                ft.Container(height=8),
                ft.Column([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("INV-001 | 2024-01-15", 
                                  size=12, weight="w500"),
                            ft.Text("Amount: ₹2,500 | Customer: ABC Corp", 
                                  size=11, color="#6B7280")
                        ], spacing=4),
                        padding=12,
                        bgcolor="#F9FAFB",
                        border_radius=6
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("INV-002 | 2024-01-16", 
                                  size=12, weight="w500"),
                            ft.Text("Amount: ₹1,800 | Customer: XYZ Ltd", 
                                  size=11, color="#6B7280")
                        ], spacing=4),
                        padding=12,
                        bgcolor="#F9FAFB",
                        border_radius=6
                    )
                ], spacing=8)
            ]),
            padding=32,
            bgcolor="white",
            border_radius=12,
            border=ft.border.all(1, "#E5E7EB"),
            animate=ft.animation.Animation(500, "easeOut")
        )

    def create_export_panel():
        """Right panel with verification and export controls"""
        return ft.Container(
            content=ft.Column([
                # Verification status
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(
                                "verified" if sim_state.verification_complete else "pending",
                                color="#10B981" if sim_state.verification_complete else "#D1D5DB"
                            ),
                            ft.Text("Verification Status", 
                                  size=14, 
                                  weight="w500",
                                  color="#1F2937")
                        ], spacing=8),
                        
                        ft.Container(height=16),
                        
                        # Checklist items
                        ft.Column([
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(
                                        "check_circle" if sim_state.revenue_match_verified else "radio_button_unchecked",
                                        size=16,
                                        color="#10B981" if sim_state.revenue_match_verified else "#D1D5DB"
                                    ),
                                    ft.Text("Revenue Target Match", size=12)
                                ], spacing=8),
                                padding=8,
                                bgcolor="#F9FAFB",
                                border_radius=4
                            ),
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(
                                        "check_circle" if sim_state.tax_logic_verified else "radio_button_unchecked",
                                        size=16,
                                        color="#10B981" if sim_state.tax_logic_verified else "#D1D5DB"
                                    ),
                                    ft.Text("Tax Logic Valid", size=12)
                                ], spacing=8),
                                padding=8,
                                bgcolor="#F9FAFB",
                                border_radius=4
                            ),
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(
                                        "check_circle" if sim_state.format_verified else "radio_button_unchecked",
                                        size=16,
                                        color="#10B981" if sim_state.format_verified else "#D1D5DB"
                                    ),
                                    ft.Text("Format Compliance", size=12)
                                ], spacing=8),
                                padding=8,
                                bgcolor="#F9FAFB",
                                border_radius=4
                            )
                        ], spacing=8)
                    ]),
                    padding=16,
                    bgcolor="#FFFFFF",
                    border_radius=8,
                    border=ft.border.all(1, "#E5E7EB")
                ),
                
                ft.Container(height=24),
                
                # Export score
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("Export Score", size=14, weight="w500"),
                            ft.Text(
                                f"{sim_state.verification_score}%", 
                                size=14, 
                                weight="bold",
                                color="#10B981" if sim_state.verification_score >= 85 else "#F59E0B"
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        
                        ft.Container(height=8),
                        
                        ft.Container(
                            content=ft.Container(
                                width=240 * (sim_state.verification_score / 100),
                                height=4,
                                bgcolor="#10B981" if sim_state.verification_score >= 85 else "#F59E0B",
                                border_radius=2
                            ),
                            width=240,
                            height=4,
                            bgcolor="#F3F4F6",
                            border_radius=2
                        ),
                        
                        ft.Container(height=4),
                        ft.Text("Export unlocks at 85%", size=10, color="#6B7280")
                    ]),
                    padding=16,
                    bgcolor="#ECFDF5" if sim_state.verification_score >= 85 else "#FEF3C7",
                    border_radius=8,
                    border=ft.border.all(1, "#D1FAE5" if sim_state.verification_score >= 85 else "#FDE68A")
                ),
                
                ft.Container(height=24),
                
                # Export settings
                ft.Text("Export Settings", size=14, weight="w500"),
                ft.Container(height=8),
                ft.Column([
                    ft.Switch(
                        ref=tax_breakdown_ref,
                        label="Include Tax Breakdown",
                        value=True
                    ),
                    ft.Switch(
                        ref=audit_trail_ref,
                        label="Add Audit Trail",
                        value=True
                    ),
                    ft.Switch(
                        ref=save_config_ref,
                        label="Save Configuration",
                        value=True
                    )
                ], spacing=8),
                
                ft.Container(height=24),
                
                # Export buttons
                ft.Column([
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon("picture_as_pdf"),
                            ft.Text("Export as PDF")
                        ], spacing=8),
                        bgcolor="#DC2626" if sim_state.can_export() else "#F3F4F6",
                        color="white" if sim_state.can_export() else "#9CA3AF",
                        disabled=not sim_state.can_export(),
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8)
                        ),
                        width=float('inf')
                    ),
                    ft.Container(height=8),
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon("table_view"),
                            ft.Text("Export as Excel")
                        ], spacing=8),
                        bgcolor="#10B981" if sim_state.can_export() else "#F3F4F6",
                        color="white" if sim_state.can_export() else "#9CA3AF",
                        disabled=not sim_state.can_export(),
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8)
                        ),
                        width=float('inf')
                    ),
                    ft.Container(height=8),
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon("format_list_bulleted"),
                            ft.Text("Export as CSV")
                        ], spacing=8),
                        bgcolor="#7C3AED" if sim_state.can_export() else "#F3F4F6",
                        color="white" if sim_state.can_export() else "#9CA3AF",
                        disabled=not sim_state.can_export(),
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8)
                        ),
                        width=float('inf')
                    )
                ])
            ]),
            width=280,
            bgcolor="white",
            border_radius=12,
            border=ft.border.all(1, "#E5E7EB"),
            padding=24,
            animate=ft.animation.Animation(500, "easeOut")
        )

    def select_template(template_type):
        """Handle template selection"""
        nonlocal selected_template
        selected_template = template_type
        sim_state.template_selected = True
        update_content()

    def start_simulation():
        """Start the simulation process"""
        sim_state.simulation_running = True
        sim_state.current_progress = 0
        update_content()
        
        # TODO: Implement actual simulation logic
        # For now, just update progress
        def update_progress(e):
            sim_state.current_progress += 20
            if sim_state.current_progress >= 100:
                sim_state.simulation_running = False
                sim_state.simulation_complete = True
                sim_state.verification_complete = True
                sim_state.export_ready = True
            update_content()
            
            if sim_state.current_progress < 100:
                page.after(500, update_progress)
                
        page.after(500, update_progress)

    def reset_template():
        """Reset to template selection"""
        sim_state.reset_template()
        update_content()

    # Main content container ref
    content_container = ft.Ref[ft.Container]()

    def update_content():
        """Update the main content based on simulation state"""
        content_container.current.content = create_simulation_layout()
        page.update()

    # Main layout
    main_layout = ft.Container(
        content=ft.Column([
            # Header
            ft.Container(
                content=ft.Row([
                    ft.Text("LedgerFlow", size=24, weight="bold", color="#1F2937"),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon("psychology", size=12, color="#059669"),
                            ft.Text("AI Engine", size=11, color="#059669")
                        ], spacing=4),
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        bgcolor="#ECFDF5",
                        border_radius=4
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=24,
                bgcolor="white",
                border=ft.border.only(bottom=ft.BorderSide(1, "#E5E7EB"))
            ),
            
            # Main content
            ft.Container(
                ref=content_container,
                content=create_simulation_layout(),
                padding=24,
                expand=True
            )
        ]),
        bgcolor="#F8FAFC",
        expand=True
    )

    return main_layout 