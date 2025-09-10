import flet as ft

def settings_view(page: ft.Page):
    # Settings state
    settings_data = {
        "company_name": "Your Company LLC",
        "company_address": "123 Business Rd, Suite 100\nCity, Country",
        "country": "India",
        "currency": "INR",
        "theme": "Light",
        "invoice_start_number": "1001",
        "default_template": "Plain Invoice",
        "realism_enabled": False,
        "realism_strength": 5,
        "customer_identity_bias": "Indian/Muslim",
        "business_style": "Electronics Shop",
        "add_random_notes": False,
        "add_random_numbers": True,
        "peak_distribution": 50
    }
    
    def save_settings(e):
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Settings saved successfully!", color="white"),
            bgcolor="#10B981"
        )
        page.snack_bar.open = True
        page.update()
    
    def reset_settings(e):
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Settings reset to default", color="white"),
            bgcolor="#6B7280"
        )
        page.snack_bar.open = True
        page.update()
    
    def export_config(e):
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Configuration exported successfully!", color="white"),
            bgcolor="#1565C0"
        )
        page.snack_bar.open = True
        page.update()
    
    def load_config(e):
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Configuration loaded successfully!", color="white"),
            bgcolor="#059669"
        )
        page.snack_bar.open = True
        page.update()
    
    def create_setting_card(title, children, icon=None):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color="#1565C0", size=24) if icon else ft.Container(),
                    ft.Text(title, size=20, weight="bold", color="#1F2937")
                ], spacing=12),
                ft.Container(height=16),
                *children
            ], spacing=0),
            padding=32,
            bgcolor="white",
            border_radius=16,
            border=ft.border.all(1, "#E5E7EB")
        )
    
    def create_form_field(label, value, hint=None, multiline=False):
        return ft.Column([
            ft.Text(label, size=14, weight="w600", color="#374151"),
            ft.Container(height=8),
            ft.TextField(
                value=value,
                hint_text=hint,
                multiline=multiline,
                min_lines=3 if multiline else 1,
                max_lines=5 if multiline else 1,
                text_style=ft.TextStyle(size=14),
                border_color="#D1D5DB",
                focused_border_color="#1565C0",
                content_padding=ft.padding.symmetric(horizontal=16, vertical=12)
            )
        ], spacing=0)
    
    def create_dropdown_field(label, value, options):
        return ft.Column([
            ft.Text(label, size=14, weight="w600", color="#374151"),
            ft.Container(height=8),
            ft.Dropdown(
                value=value,
                options=[ft.dropdown.Option(opt, opt) for opt in options],
                text_style=ft.TextStyle(size=14),
                border_color="#D1D5DB",
                focused_border_color="#1565C0",
                content_padding=ft.padding.symmetric(horizontal=16, vertical=12)
            )
        ], spacing=0)
    
    def create_switch_field(label, description, value):
        return ft.Row([
            ft.Column([
                ft.Text(label, size=14, weight="w600", color="#374151"),
                ft.Text(description, size=12, color="#6B7280")
            ], spacing=4, expand=True),
            ft.Switch(value=value, active_color="#1565C0")
        ], alignment="spaceBetween")
    
    def create_slider_field(label, description, value, min_val, max_val):
        return ft.Column([
            ft.Row([
                ft.Text(label, size=14, weight="w600", color="#374151"),
                ft.Text(str(value), size=14, weight="bold", color="#1565C0")
            ], alignment="spaceBetween"),
            ft.Text(description, size=12, color="#6B7280"),
            ft.Container(height=8),
            ft.Slider(
                value=value,
                min=min_val,
                max=max_val,
                divisions=max_val - min_val,
                active_color="#1565C0",
                inactive_color="#E5E7EB"
            )
        ], spacing=0)
    
    # Header
    header = ft.Container(
        content=ft.Column([
            ft.Text("Settings", size=32, weight="bold", color="#1F2937"),
            ft.Text("Configure your invoice generation preferences and business details", 
                   size=16, color="#6B7280")
        ], spacing=8),
        padding=ft.padding.only(bottom=32)
    )
    
    # Company & General Settings
    company_section = create_setting_card(
        "Company & General", 
        [
            ft.Row([
                create_form_field("Company Name", settings_data["company_name"]),
                ft.Container(width=24),
                create_form_field("Invoice Starting Number", settings_data["invoice_start_number"])
            ], alignment="start"),
            
            ft.Container(height=20),
            
            create_form_field(
                "Company Address", 
                settings_data["company_address"], 
                "Enter your business address",
                multiline=True
            ),
            
            ft.Container(height=20),
            
            ft.Row([
                create_dropdown_field(
                    "Country", 
                    settings_data["country"],
                    ["India", "Bahrain", "United States", "United Kingdom", "Canada"]
                ),
                ft.Container(width=24),
                create_dropdown_field(
                    "Default Currency",
                    settings_data["currency"], 
                    ["INR", "BHD", "USD", "EUR", "GBP"]
                )
            ], alignment="start"),
            
            ft.Container(height=20),
            
            ft.Row([
                ft.Column([
                    ft.Text("Upload Logo", size=14, weight="w600", color="#374151"),
                    ft.Container(height=8),
                    ft.OutlinedButton(
                        "Choose File",
                        icon=ft.Icon("upload"),
                        height=40,
                        style=ft.ButtonStyle(color={"": "#1565C0"})
                    )
                ], expand=True),
                ft.Container(width=24),
                ft.Column([
                    ft.Text("Upload Signature", size=14, weight="w600", color="#374151"),
                    ft.Container(height=8),
                    ft.OutlinedButton(
                        "Choose File",
                        icon=ft.Icon("upload"),
                        height=40,
                        style=ft.ButtonStyle(color={"": "#1565C0"})
                    )
                ], expand=True)
            ], alignment="start")
        ],
        icon="business"
    )
    
    # Theme Settings
    theme_section = create_setting_card(
        "Appearance",
        [
            ft.Row([
                ft.Column([
                    ft.Text("Theme", size=14, weight="w600", color="#374151"),
                    ft.Container(height=12),
                    ft.Row([
                        ft.Container(
                            content=ft.Column([
                                ft.Icon("light_mode", color="#1565C0", size=20),
                                ft.Text("Light", size=12, color="#374151")
                            ], horizontal_alignment="center", spacing=8),
                            padding=16,
                            bgcolor="#F3F4F6" if settings_data["theme"] == "Light" else "white",
                            border_radius=12,
                            border=ft.border.all(2, "#1565C0" if settings_data["theme"] == "Light" else "#E5E7EB"),
                            width=80
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Icon("dark_mode", color="#6B7280", size=20),
                                ft.Text("Dark", size=12, color="#374151")
                            ], horizontal_alignment="center", spacing=8),
                            padding=16,
                            bgcolor="white",
                            border_radius=12,
                            border=ft.border.all(2, "#E5E7EB"),
                            width=80
                        )
                    ], spacing=16)
                ], expand=True),
                
                create_dropdown_field(
                    "Default Invoice Template",
                    settings_data["default_template"],
                    ["Plain Invoice", "GST Invoice", "VAT Invoice"]
                )
            ], alignment="start")
        ],
        icon="palette"
    )
    
    # Realism Engine Settings
    realism_section = create_setting_card(
        "Advanced & Realism Engine",
        [
            create_switch_field(
                "Enable Realism Engine",
                "Generate ultra-realistic invoices with advanced algorithms",
                settings_data["realism_enabled"]
            ),
            
            ft.Container(height=24),
            ft.Divider(color="#E5E7EB"),
            ft.Container(height=24),
            
            ft.Text("Realism Configuration", size=16, weight="bold", color="#374151"),
            ft.Container(height=16),
            
            create_slider_field(
                "Realism Strength",
                "Controls how realistic the generated data appears (1-10 scale)",
                settings_data["realism_strength"],
                1, 10
            ),
            
            ft.Container(height=20),
            
            ft.Row([
                create_dropdown_field(
                    "Business Style",
                    settings_data["business_style"],
                    ["Electronics Shop", "Medical Store", "Grocery Store", "Textile Business", 
                     "Wholesale", "Retail", "Luxury Store"]
                ),
                ft.Container(width=24),
                create_dropdown_field(
                    "Customer Identity Bias",
                    settings_data["customer_identity_bias"],
                    ["Indian/Muslim", "Western", "Mixed", "Regional"]
                )
            ], alignment="start"),
            
            ft.Container(height=20),
            
            ft.Text("Additional Features", size=14, weight="w600", color="#374151"),
            ft.Container(height=12),
            
            create_switch_field(
                "Add Random Invoice Notes",
                "Include realistic payment terms and notes",
                settings_data["add_random_notes"]
            ),
            
            ft.Container(height=16),
            
            create_switch_field(
                "Add Random Invoice Numbers", 
                "Generate realistic invoice numbering patterns",
                settings_data["add_random_numbers"]
            ),
            
            ft.Container(height=20),
            
            create_slider_field(
                "Peak Distribution Tolerance",
                "Controls variance in invoice amounts (50% - 200%)",
                settings_data["peak_distribution"],
                50, 200
            ),
            
            ft.Container(height=24),
            
            ft.Text("Historical Data Upload", size=14, weight="w600", color="#374151"),
            ft.Container(height=8),
            ft.Text("Upload sales CSV for realism calibration", size=12, color="#6B7280"),
            ft.Container(height=12),
            
            ft.Container(
                content=ft.Column([
                    ft.Icon("cloud_upload", color="#6B7280", size=32),
                    ft.Text("Upload Historical Sales CSV", size=14, color="#6B7280"),
                    ft.Text("(for realism calibration)", size=12, color="#9CA3AF")
                ], horizontal_alignment="center", spacing=8),
                padding=32,
                border=ft.border.all(2, "#E5E7EB"),
                border_radius=12,
                bgcolor="#F9FAFB"
            )
        ],
        icon="auto_awesome"
    )
    
    # License Section
    license_section = create_setting_card(
        "License",
        [
            ft.Row([
                ft.Column([
                    ft.Text("License Key Status", size=14, weight="w600", color="#374151"),
                    ft.Container(height=8),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon("check_circle", color="#10B981", size=16),
                            ft.Text("Active", size=14, color="#10B981", weight="w500")
                        ], spacing=8),
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        bgcolor="#ECFDF5",
                        border_radius=16,
                        border=ft.border.all(1, "#D1FAE5")
                    )
                ], expand=True),
                
                ft.ElevatedButton(
                    "Manage License",
                    bgcolor="#1565C0",
                    color="white",
                    height=40,
                    style=ft.ButtonStyle(text_style=ft.TextStyle(size=14, weight="w500"))
                )
            ], alignment="spaceBetween")
        ],
        icon="key"
    )
    
    # Action Buttons
    action_buttons = ft.Container(
        content=ft.Row([
            ft.OutlinedButton(
                "Export Config Snapshot",
                icon=ft.Icon("download"),
                height=48,
                style=ft.ButtonStyle(
                    text_style=ft.TextStyle(size=14, weight="w500"),
                    color={"": "#6B7280"}
                ),
                on_click=export_config
            ),
            
            ft.OutlinedButton(
                "Load Previous Config",
                icon=ft.Icon("upload"),
                height=48,
                style=ft.ButtonStyle(
                    text_style=ft.TextStyle(size=14, weight="w500"),
                    color={"": "#6B7280"}
                ),
                on_click=load_config
            ),
            
            ft.Container(expand=True),
            
            ft.OutlinedButton(
                "Reset to Default",
                height=48,
                style=ft.ButtonStyle(
                    text_style=ft.TextStyle(size=14, weight="w500"),
                    color={"": "#DC2626"}
                ),
                on_click=reset_settings
            ),
            
            ft.ElevatedButton(
                "Save Settings",
                icon=ft.Icon("save"),
                bgcolor="#10B981",
                color="white",
                height=48,
                style=ft.ButtonStyle(text_style=ft.TextStyle(size=16, weight="w600")),
                on_click=save_settings
            )
        ], spacing=16),
        padding=ft.padding.only(top=32)
    )
    
    # Main content with scroll
    content = ft.Column([
        header,
        company_section,
        ft.Container(height=24),
        theme_section,
        ft.Container(height=24),
        realism_section,
        ft.Container(height=24),
        license_section,
        action_buttons
    ], spacing=0, scroll=ft.ScrollMode.AUTO)
    
    return ft.Container(
        content=content,
        padding=40,
        bgcolor="#F8FAFC",
        expand=True
    ) 