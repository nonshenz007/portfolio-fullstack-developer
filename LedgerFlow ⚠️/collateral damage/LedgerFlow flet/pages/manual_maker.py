# This file will contain the UI for the manual maker page. 

import flet as ft
from datetime import datetime
import random
from utils.invoice_generator import get_gst_rate, get_vat_rate, calculate_gst_breakdown, generate_gstin, generate_vat_number, amount_in_words_inr

def manual_maker_view(page: ft.Page):
    # State variables
    selected_template = "Plain"
    items_list = []
    preview_visible = False
    
    # Form field references
    invoice_number_field = None
    customer_name_field = None
    customer_address_field = None
    invoice_date_field = None
    due_date_field = None
    item_name_field = None
    item_qty_field = None
    item_rate_field = None
    item_hsn_field = None
    notes_field = None
    
    def get_template_color(template):
        colors = {
            "Plain": "#6B7280",
            "GST": "#059669",
            "VAT": "#DC2626"
        }
        return colors.get(template, "#6B7280")
    
    def select_template(template_type):
        def handler(e):
            nonlocal selected_template
            selected_template = template_type
            update_template_selection()
            update_form_visibility()
        return handler
    
    def update_template_selection():
        for btn in [plain_btn, gst_btn, vat_btn]:
            template = btn.data
            is_selected = template == selected_template
            
            btn.bgcolor = get_template_color(template) if is_selected else "white"
            btn.content.color = "white" if is_selected else get_template_color(template)
            btn.border = ft.border.all(2, get_template_color(template))
        
        # Update currency based on template
        if selected_template == "VAT":
            item_rate_field.prefix_text = "BD"
        else:
            item_rate_field.prefix_text = "₹"
            
        page.update()
    
    def update_form_visibility():
        # Show/hide GST/VAT specific fields
        if selected_template == "GST":
            gst_fields_container.visible = True
            vat_fields_container.visible = False
        elif selected_template == "VAT":
            gst_fields_container.visible = False
            vat_fields_container.visible = True
        else:
            gst_fields_container.visible = False
            vat_fields_container.visible = False
        
        page.update()
    
    def add_item(e):
        # Validate item fields
        if not all([item_name_field.value, item_qty_field.value, item_rate_field.value]):
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Please fill in all item fields", color="white"),
                bgcolor="#F44336"
            )
            page.snack_bar.open = True
            page.update()
            return
        
        try:
            qty = float(item_qty_field.value)
            rate = float(item_rate_field.value)
            if qty <= 0 or rate <= 0:
                raise ValueError("Values must be positive")
        except ValueError:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Please enter valid quantity and rate", color="white"),
                bgcolor="#F44336"
            )
            page.snack_bar.open = True
            page.update()
            return
        
        # Create item
        item_amount = qty * rate
        item = {
            "name": item_name_field.value,
            "qty": qty,
            "rate": rate,
            "amount": round(item_amount, 2),
            "hsn_code": item_hsn_field.value or "9999"
        }
        
        # Add tax calculations based on template
        if selected_template == "GST":
            gst_rate = get_gst_rate(item["name"], "General")
            gst_breakdown = calculate_gst_breakdown(item_amount, gst_rate)
            item.update(gst_breakdown)
            item["total_with_tax"] = round(item_amount + gst_breakdown["total_gst"], 2)
        elif selected_template == "VAT":
            vat_rate = get_vat_rate(item["name"], "General")
            vat_amount = round(item_amount * (vat_rate / 100), 2)
            item.update({
                "vat_rate": vat_rate,
                "vat_amount": vat_amount,
                "total_with_tax": round(item_amount + vat_amount, 2)
            })
        else:
            item["total_with_tax"] = round(item_amount, 2)
        
        items_list.append(item)
        
        # Clear item fields
        item_name_field.value = ""
        item_qty_field.value = ""
        item_rate_field.value = ""
        item_hsn_field.value = ""
        
        update_items_table()
        update_totals()
        page.update()
    
    def remove_item(index):
        def handler(e):
            items_list.pop(index)
            update_items_table()
            update_totals()
            page.update()
        return handler
    
    def update_items_table():
        items_table.controls.clear()
        
        if not items_list:
            items_table.controls.append(
                ft.Container(
                    content=ft.Text("No items added yet", size=14, color="#9CA3AF"),
                    padding=20,
                    alignment=ft.alignment.center
                )
            )
        else:
            # Header
            header_row = ft.Row([
                ft.Text("Item", size=12, weight="bold", color="#6B7280", expand=3),
                ft.Text("HSN", size=12, weight="bold", color="#6B7280", expand=1),
                ft.Text("Qty", size=12, weight="bold", color="#6B7280", expand=1),
                ft.Text("Rate", size=12, weight="bold", color="#6B7280", expand=1),
                ft.Text("Amount", size=12, weight="bold", color="#6B7280", expand=1),
                ft.Container(width=40)  # Actions column
            ], spacing=8)
            
            items_table.controls.append(
                ft.Container(
                    content=header_row,
                    padding=ft.padding.symmetric(horizontal=16, vertical=12),
                    bgcolor="#F9FAFB",
                    border_radius=ft.border_radius.only(top_left=8, top_right=8)
                )
            )
            
            # Item rows
            for i, item in enumerate(items_list):
                currency = "BD" if selected_template == "VAT" else "₹"
                
                item_row = ft.Row([
                    ft.Text(item["name"], size=14, color="#1F2937", expand=3),
                    ft.Text(item["hsn_code"], size=14, color="#6B7280", expand=1),
                    ft.Text(str(int(item["qty"])), size=14, color="#6B7280", expand=1),
                    ft.Text(f"{currency}{item['rate']:.2f}", size=14, color="#6B7280", expand=1),
                    ft.Text(f"{currency}{item['amount']:.2f}", size=14, weight="w600", color="#10B981", expand=1),
                    ft.IconButton(
                        icon="delete",
                        icon_color="#DC2626",
                        icon_size=16,
                        on_click=remove_item(i)
                    )
                ], spacing=8)
                
                items_table.controls.append(
                    ft.Container(
                        content=item_row,
                        padding=ft.padding.symmetric(horizontal=16, vertical=12),
                        border=ft.border.only(bottom=ft.BorderSide(1, "#E5E7EB"))
                    )
                )
    
    def update_totals():
        if not items_list:
            totals_container.visible = False
            return
        
        totals_container.visible = True
        subtotal = sum(item["amount"] for item in items_list)
        currency = "BD" if selected_template == "VAT" else "₹"
        
        # Clear existing totals
        totals_column.controls.clear()
        
        # Subtotal
        totals_column.controls.append(
            ft.Row([
                ft.Text("Subtotal:", size=14, color="#6B7280"),
                ft.Text(f"{currency}{subtotal:.2f}", size=14, weight="w600", color="#1F2937")
            ], alignment="spaceBetween")
        )
        
        # Tax calculations
        if selected_template == "GST":
            total_cgst = sum(item.get("cgst", 0) for item in items_list)
            total_sgst = sum(item.get("sgst", 0) for item in items_list)
            total_gst = total_cgst + total_sgst
            grand_total = subtotal + total_gst
            
            totals_column.controls.extend([
                ft.Row([
                    ft.Text("CGST:", size=14, color="#6B7280"),
                    ft.Text(f"{currency}{total_cgst:.2f}", size=14, color="#1F2937")
                ], alignment="spaceBetween"),
                ft.Row([
                    ft.Text("SGST:", size=14, color="#6B7280"),
                    ft.Text(f"{currency}{total_sgst:.2f}", size=14, color="#1F2937")
                ], alignment="spaceBetween"),
                ft.Divider(color="#E5E7EB"),
                ft.Row([
                    ft.Text("Total:", size=16, weight="bold", color="#1F2937"),
                    ft.Text(f"{currency}{grand_total:.2f}", size=16, weight="bold", color="#10B981")
                ], alignment="spaceBetween")
            ])
            
        elif selected_template == "VAT":
            total_vat = sum(item.get("vat_amount", 0) for item in items_list)
            grand_total = subtotal + total_vat
            
            totals_column.controls.extend([
                ft.Row([
                    ft.Text("VAT:", size=14, color="#6B7280"),
                    ft.Text(f"{currency}{total_vat:.2f}", size=14, color="#1F2937")
                ], alignment="spaceBetween"),
                ft.Divider(color="#E5E7EB"),
                ft.Row([
                    ft.Text("Total:", size=16, weight="bold", color="#1F2937"),
                    ft.Text(f"{currency}{grand_total:.2f}", size=16, weight="bold", color="#10B981")
                ], alignment="spaceBetween")
            ])
        else:
            totals_column.controls.extend([
                ft.Divider(color="#E5E7EB"),
                ft.Row([
                    ft.Text("Total:", size=16, weight="bold", color="#1F2937"),
                    ft.Text(f"{currency}{subtotal:.2f}", size=16, weight="bold", color="#10B981")
                ], alignment="spaceBetween")
            ])
        
        page.update()
    
    def save_invoice(e):
        # Validate required fields
        if not all([invoice_number_field.value, customer_name_field.value, invoice_date_field.value]):
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Please fill in invoice number, customer name, and date", color="white"),
                bgcolor="#F44336"
            )
            page.snack_bar.open = True
            page.update()
            return
        
        if not items_list:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Please add at least one item", color="white"),
                bgcolor="#F44336"
            )
            page.snack_bar.open = True
            page.update()
            return
        
        # Success message
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Invoice {invoice_number_field.value} saved successfully!", color="white"),
            bgcolor="#10B981"
        )
        page.snack_bar.open = True
        page.update()
    
    def preview_invoice(e):
        nonlocal preview_visible
        if not items_list:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Please add at least one item to preview", color="white"),
                bgcolor="#F44336"
            )
            page.snack_bar.open = True
            page.update()
            return
        
        preview_visible = not preview_visible
        preview_container.visible = preview_visible
        preview_btn.text = "Hide Preview" if preview_visible else "Show Preview"
        page.update()
    
    # Create form fields
    invoice_number_field = ft.TextField(
        label="Invoice Number",
        value=f"INV-{random.randint(10000, 99999)}",
        border_color="#D1D5DB",
        focused_border_color="#1565C0"
    )
    
    customer_name_field = ft.TextField(
        label="Customer Name",
        border_color="#D1D5DB",
        focused_border_color="#1565C0"
    )
    
    customer_address_field = ft.TextField(
        label="Customer Address",
        multiline=True,
        min_lines=2,
        max_lines=3,
        border_color="#D1D5DB",
        focused_border_color="#1565C0"
    )
    
    invoice_date_field = ft.TextField(
        label="Invoice Date",
        value=datetime.now().strftime("%Y-%m-%d"),
        border_color="#D1D5DB",
        focused_border_color="#1565C0"
    )
    
    due_date_field = ft.TextField(
        label="Due Date",
        border_color="#D1D5DB",
        focused_border_color="#1565C0"
    )
    
    # Item entry fields
    item_name_field = ft.TextField(
        label="Item Name",
        border_color="#D1D5DB",
        focused_border_color="#1565C0",
        expand=3
    )
    
    item_qty_field = ft.TextField(
        label="Quantity",
        border_color="#D1D5DB",
        focused_border_color="#1565C0",
        width=100
    )
    
    item_rate_field = ft.TextField(
        label="Rate",
        prefix_text="₹",
        border_color="#D1D5DB",
        focused_border_color="#1565C0",
        width=120
    )
    
    item_hsn_field = ft.TextField(
        label="HSN Code",
        border_color="#D1D5DB",
        focused_border_color="#1565C0",
        width=100
    )
    
    notes_field = ft.TextField(
        label="Notes (Optional)",
        multiline=True,
        min_lines=2,
        max_lines=3,
        border_color="#D1D5DB",
        focused_border_color="#1565C0"
    )
    
    # Template selection buttons
    plain_btn = ft.Container(
        content=ft.Text("Plain Invoice", size=14, weight="w600"),
        padding=ft.padding.symmetric(horizontal=20, vertical=12),
        border_radius=8,
        on_click=select_template("Plain"),
        data="Plain"
    )
    
    gst_btn = ft.Container(
        content=ft.Text("GST Invoice", size=14, weight="w600"),
        padding=ft.padding.symmetric(horizontal=20, vertical=12),
        border_radius=8,
        on_click=select_template("GST"),
        data="GST"
    )
    
    vat_btn = ft.Container(
        content=ft.Text("VAT Invoice", size=14, weight="w600"),
        padding=ft.padding.symmetric(horizontal=20, vertical=12),
        border_radius=8,
        on_click=select_template("VAT"),
        data="VAT"
    )
    
    # GST specific fields
    gst_fields_container = ft.Container(
        content=ft.Column([
            ft.Text("GST Details", size=16, weight="bold", color="#374151"),
            ft.Container(height=12),
            ft.Row([
                ft.TextField(
                    label="Your GSTIN",
                    value=generate_gstin(),
                    border_color="#D1D5DB",
                    focused_border_color="#1565C0",
                    expand=True
                ),
                ft.Container(width=16),
                ft.TextField(
                    label="Customer GSTIN (Optional)",
                    border_color="#D1D5DB",
                    focused_border_color="#1565C0",
                    expand=True
                )
            ])
        ]),
        visible=False
    )
    
    # VAT specific fields
    vat_fields_container = ft.Container(
        content=ft.Column([
            ft.Text("VAT Details", size=16, weight="bold", color="#374151"),
            ft.Container(height=12),
            ft.Row([
                ft.TextField(
                    label="Your VAT Registration",
                    value=generate_vat_number(),
                    border_color="#D1D5DB",
                    focused_border_color="#1565C0",
                    expand=True
                ),
                ft.Container(width=16),
                ft.TextField(
                    label="Customer VAT Registration (Optional)",
                    border_color="#D1D5DB",
                    focused_border_color="#1565C0",
                    expand=True
                )
            ])
        ]),
        visible=False
    )
    
    # Items table and totals
    items_table = ft.Column(spacing=0)
    totals_column = ft.Column(spacing=8)
    totals_container = ft.Container(
        content=totals_column,
        padding=20,
        bgcolor="#F9FAFB",
        border_radius=8,
        visible=False
    )
    
    # Preview container
    preview_container = ft.Container(
        content=ft.Text("Invoice preview will appear here", size=14, color="#6B7280"),
        padding=20,
        bgcolor="#F9FAFB",
        border_radius=8,
        visible=False
    )
    
    # Preview button
    preview_btn = ft.OutlinedButton(
        "Show Preview",
        icon=ft.Icon("preview"),
        on_click=preview_invoice
    )
    
    # Initialize template selection
    update_template_selection()
    update_form_visibility()
    update_items_table()
    
    # Main layout
    return ft.Container(
        content=ft.Row([
            # Left panel - Form
            ft.Container(
                content=ft.Column([
                    # Header
                    ft.Text("Create Invoice", size=28, weight="bold", color="#1F2937"),
                    ft.Text("Fill in the details below to create a new invoice", size=14, color="#6B7280"),
                    
                    ft.Container(height=24),
                    
                    # Template selection
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Invoice Template", size=16, weight="bold", color="#374151"),
                            ft.Container(height=12),
                            ft.Row([plain_btn, gst_btn, vat_btn], spacing=12)
                        ]),
                        padding=20,
                        bgcolor="white",
                        border_radius=12,
                        border=ft.border.all(1, "#E5E7EB")
                    ),
                    
                    ft.Container(height=20),
                    
                    # Basic invoice details
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Invoice Details", size=16, weight="bold", color="#374151"),
                            ft.Container(height=16),
                            ft.Row([
                                invoice_number_field,
                                ft.Container(width=16),
                                invoice_date_field,
                                ft.Container(width=16),
                                due_date_field
                            ]),
                            ft.Container(height=16),
                            customer_name_field,
                            ft.Container(height=16),
                            customer_address_field
                        ]),
                        padding=20,
                        bgcolor="white",
                        border_radius=12,
                        border=ft.border.all(1, "#E5E7EB")
                    ),
                    
                    ft.Container(height=20),
                    
                    # GST/VAT specific fields
                    gst_fields_container,
                    vat_fields_container,
                    
                    # Add spacing when GST/VAT fields are visible
                    ft.Container(height=20),
                    
                    # Item entry
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Add Items", size=16, weight="bold", color="#374151"),
                            ft.Container(height=16),
                            ft.Row([
                                item_name_field,
                                ft.Container(width=12),
                                item_hsn_field,
                                ft.Container(width=12),
                                item_qty_field,
                                ft.Container(width=12),
                                item_rate_field,
                                ft.Container(width=12),
                                ft.ElevatedButton(
                                    "Add",
                                    bgcolor="#1565C0",
                                    color="white",
                                    on_click=add_item
                                )
                            ], alignment="end")
                        ]),
                        padding=20,
                        bgcolor="white",
                        border_radius=12,
                        border=ft.border.all(1, "#E5E7EB")
                    ),
                    
                    ft.Container(height=20),
                    
                    # Notes
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Additional Notes", size=16, weight="bold", color="#374151"),
                            ft.Container(height=16),
                            notes_field
                        ]),
                        padding=20,
                        bgcolor="white",
                        border_radius=12,
                        border=ft.border.all(1, "#E5E7EB")
                    ),
                    
                    ft.Container(height=24),
                    
                    # Action buttons
                    ft.Row([
                        preview_btn,
                        ft.Container(expand=True),
                        ft.OutlinedButton(
                            "Clear All",
                            icon=ft.Icon("clear"),
                            style=ft.ButtonStyle(color={"": "#DC2626"})
                        ),
                        ft.Container(width=12),
                        ft.ElevatedButton(
                            "Save Invoice",
                            icon=ft.Icon("save"),
                            bgcolor="#10B981",
                            color="white",
                            on_click=save_invoice
                        )
                    ])
                ], scroll=ft.ScrollMode.AUTO),
                width=600,
                padding=32
            ),
            
            # Right panel - Items and preview
            ft.Container(
                content=ft.Column([
                    # Items list
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Invoice Items", size=20, weight="bold", color="#1F2937"),
                            ft.Container(height=16),
                            items_table
                        ]),
                        padding=20,
                        bgcolor="white",
                        border_radius=12,
                        border=ft.border.all(1, "#E5E7EB"),
                        height=300
                    ),
                    
                    ft.Container(height=16),
                    
                    # Totals
                    totals_container,
                    
                    ft.Container(height=16),
                    
                    # Preview
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Invoice Preview", size=20, weight="bold", color="#1F2937"),
                            ft.Container(height=16),
                            preview_container
                        ]),
                        padding=20,
                        bgcolor="white",
                        border_radius=12,
                        border=ft.border.all(1, "#E5E7EB"),
                        expand=True
                    )
                ], spacing=0),
                expand=True,
                padding=32
            )
        ], spacing=0),
        bgcolor="#F8FAFC",
        expand=True
    ) 