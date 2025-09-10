import flet as ft
from datetime import datetime, timedelta
import random
from utils.invoice_generator import generate_plain_invoices

def invoices_view(page: ft.Page):
    # Sample invoice data for demo (in real app, this would come from a database)
    sample_invoices = [
        {
            "invoice_number": "INV-45123",
            "date": "2024-01-15",
            "customer_name": "Muhammad Irfan",
            "template_type": "GST",
            "total": 2850.75,
            "currency_symbol": "₹",
            "status": "Paid",
            "items_count": 3
        },
        {
            "invoice_number": "INV-45124", 
            "date": "2024-01-16",
            "customer_name": "Aaliya Sharma",
            "template_type": "Plain",
            "total": 1250.00,
            "currency_symbol": "₹",
            "status": "Pending",
            "items_count": 2
        },
        {
            "invoice_number": "INV-45125",
            "date": "2024-01-17",
            "customer_name": "Omar Hassan",
            "template_type": "VAT",
            "total": 890.50,
            "currency_symbol": "BD",
            "status": "Paid",
            "items_count": 4
        },
        {
            "invoice_number": "INV-45126",
            "date": "2024-01-18",
            "customer_name": "Priya Verma",
            "template_type": "GST",
            "total": 4250.25,
            "currency_symbol": "₹",
            "status": "Overdue",
            "items_count": 6
        },
        {
            "invoice_number": "INV-45127",
            "date": "2024-01-19",
            "customer_name": "Zara Ahmed",
            "template_type": "Plain",
            "total": 850.00,
            "currency_symbol": "₹",
            "status": "Draft",
            "items_count": 1
        }
    ]
    
    # State variables
    filtered_invoices = sample_invoices.copy()
    selected_filter = "All"
    search_query = ""
    
    def get_status_color(status):
        colors = {
            "Paid": "#10B981",
            "Pending": "#F59E0B", 
            "Overdue": "#DC2626",
            "Draft": "#6B7280"
        }
        return colors.get(status, "#6B7280")
    
    def get_template_color(template):
        colors = {
            "Plain": "#6B7280",
            "GST": "#059669",
            "VAT": "#DC2626"
        }
        return colors.get(template, "#6B7280")
    
    def filter_invoices(filter_type):
        def handler(e):
            nonlocal selected_filter, filtered_invoices
            selected_filter = filter_type
            apply_filters()
            update_filter_buttons()
            update_invoice_table()
        return handler
    
    def search_invoices(e):
        nonlocal search_query, filtered_invoices
        search_query = e.control.value.lower()
        apply_filters()
        update_invoice_table()
    
    def apply_filters():
        nonlocal filtered_invoices
        filtered_invoices = sample_invoices.copy()
        
        # Apply status filter
        if selected_filter != "All":
            filtered_invoices = [inv for inv in filtered_invoices if inv["status"] == selected_filter]
        
        # Apply search filter
        if search_query:
            filtered_invoices = [
                inv for inv in filtered_invoices 
                if (search_query in inv["invoice_number"].lower() or 
                    search_query in inv["customer_name"].lower() or
                    search_query in inv["template_type"].lower())
            ]
    
    def export_invoice(invoice, format_type):
        def handler(e):
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Exporting {invoice['invoice_number']} as {format_type}...", color="white"),
                bgcolor="#1565C0"
            )
            page.snack_bar.open = True
            page.update()
        return handler
    
    def view_invoice_details(invoice):
        def handler(e):
            # TODO: Implement invoice detail view
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Opening details for {invoice['invoice_number']}", color="white"),
                bgcolor="#1565C0"
            )
            page.snack_bar.open = True
            page.update()
        return handler
    
    def create_filter_button(text, count=None):
        is_active = selected_filter == text
        display_text = f"{text} ({count})" if count is not None else text
        
        return ft.Container(
            content=ft.Text(
                display_text,
                size=14,
                weight="w600" if is_active else "w500",
                color="white" if is_active else "#374151"
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            bgcolor="#1565C0" if is_active else "white",
            border_radius=20,
            border=ft.border.all(1, "#1565C0" if is_active else "#D1D5DB"),
            on_click=filter_invoices(text)
        )
    
    def update_filter_buttons():
        filter_row.controls.clear()
        
        # Count invoices by status
        status_counts = {}
        for inv in sample_invoices:
            status = inv["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Add filter buttons
        filter_row.controls.extend([
            create_filter_button("All", len(sample_invoices)),
            create_filter_button("Paid", status_counts.get("Paid", 0)),
            create_filter_button("Pending", status_counts.get("Pending", 0)),
            create_filter_button("Overdue", status_counts.get("Overdue", 0)),
            create_filter_button("Draft", status_counts.get("Draft", 0))
        ])
        page.update()
    
    def create_invoice_row(invoice):
        return ft.Container(
            content=ft.Row([
                # Invoice number and date
                ft.Column([
                    ft.Text(invoice["invoice_number"], size=14, weight="w600", color="#1F2937"),
                    ft.Text(invoice["date"], size=12, color="#6B7280")
                ], spacing=4, tight=True),
                
                # Customer name
                ft.Container(
                    content=ft.Text(invoice["customer_name"], size=14, color="#374151"),
                    width=180
                ),
                
                # Template type badge
                ft.Container(
                    content=ft.Text(
                        invoice["template_type"], 
                        size=12, 
                        weight="w500", 
                        color="white"
                    ),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    bgcolor=get_template_color(invoice["template_type"]),
                    border_radius=12,
                    width=60,
                    alignment=ft.alignment.center
                ),
                
                # Status badge
                ft.Container(
                    content=ft.Text(
                        invoice["status"], 
                        size=12, 
                        weight="w500", 
                        color="white"
                    ),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    bgcolor=get_status_color(invoice["status"]),
                    border_radius=12,
                    width=80,
                    alignment=ft.alignment.center
                ),
                
                # Amount
                ft.Container(
                    content=ft.Text(
                        f"{invoice['currency_symbol']}{invoice['total']:,.2f}", 
                        size=14, 
                        weight="w600", 
                        color="#10B981"
                    ),
                    width=120,
                    alignment=ft.alignment.center_right
                ),
                
                # Actions
                ft.Row([
                    ft.IconButton(
                        icon="visibility",
                        icon_color="#6B7280",
                        icon_size=18,
                        tooltip="View Details",
                        on_click=view_invoice_details(invoice)
                    ),
                    ft.PopupMenuButton(
                        items=[
                            ft.PopupMenuItem(
                                content=ft.Row([
                                    ft.Icon("picture_as_pdf", size=16),
                                    ft.Text("Export PDF", size=14)
                                ], spacing=8),
                                on_click=export_invoice(invoice, "PDF")
                            ),
                            ft.PopupMenuItem(
                                content=ft.Row([
                                    ft.Icon("table_chart", size=16),
                                    ft.Text("Export Excel", size=14)
                                ], spacing=8),
                                on_click=export_invoice(invoice, "Excel")
                            ),
                            ft.PopupMenuItem(
                                content=ft.Row([
                                    ft.Icon("download", size=16),
                                    ft.Text("Export CSV", size=14)
                                ], spacing=8),
                                on_click=export_invoice(invoice, "CSV")
                            ),
                            ft.PopupMenuItem(),  # Divider
                            ft.PopupMenuItem(
                                content=ft.Row([
                                    ft.Icon("edit", size=16),
                                    ft.Text("Edit", size=14)
                                ], spacing=8)
                            ),
                            ft.PopupMenuItem(
                                content=ft.Row([
                                    ft.Icon("delete", size=16, color="#DC2626"),
                                    ft.Text("Delete", size=14, color="#DC2626")
                                ], spacing=8)
                            )
                        ],
                        icon="more_vert",
                        icon_size=18
                    )
                ], spacing=0)
            ], alignment="center", spacing=16),
            padding=ft.padding.symmetric(horizontal=24, vertical=16),
            bgcolor="white",
            border_radius=8,
            border=ft.border.all(1, "#E5E7EB"),
            margin=ft.margin.only(bottom=8)
        )
    
    def update_invoice_table():
        invoice_list.controls.clear()
        
        if not filtered_invoices:
            # Empty state
            invoice_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon("description", size=64, color="#D1D5DB"),
                        ft.Text("No invoices found", size=18, weight="w600", color="#6B7280"),
                        ft.Text("Try adjusting your filters or create your first invoice", size=14, color="#9CA3AF")
                    ], horizontal_alignment="center", spacing=16),
                    padding=64,
                    alignment=ft.alignment.center
                )
            )
        else:
            # Add header row
            invoice_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text("Invoice", size=12, weight="bold", color="#6B7280"),
                        ft.Container(
                            content=ft.Text("Customer", size=12, weight="bold", color="#6B7280"),
                            width=180
                        ),
                        ft.Container(
                            content=ft.Text("Type", size=12, weight="bold", color="#6B7280"),
                            width=60,
                            alignment=ft.alignment.center
                        ),
                        ft.Container(
                            content=ft.Text("Status", size=12, weight="bold", color="#6B7280"),
                            width=80,
                            alignment=ft.alignment.center
                        ),
                        ft.Container(
                            content=ft.Text("Amount", size=12, weight="bold", color="#6B7280"),
                            width=120,
                            alignment=ft.alignment.center_right
                        ),
                        ft.Text("Actions", size=12, weight="bold", color="#6B7280")
                    ], alignment="center", spacing=16),
                    padding=ft.padding.symmetric(horizontal=24, vertical=12),
                    bgcolor="#F9FAFB",
                    border_radius=ft.border_radius.only(top_left=8, top_right=8)
                )
            )
            
            # Add invoice rows
            for invoice in filtered_invoices:
                invoice_list.controls.append(create_invoice_row(invoice))
        
        page.update()
    
    # Create UI components
    search_field = ft.TextField(
        hint_text="Search invoices, customers, or types...",
        prefix_icon="search",
        border_color="#D1D5DB",
        focused_border_color="#1565C0",
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        on_change=search_invoices,
        width=400
    )
    
    filter_row = ft.Row(spacing=12)
    
    invoice_list = ft.Column(spacing=0)
    
    # Initialize components
    update_filter_buttons()
    update_invoice_table()
    
    # Main layout
    return ft.Container(
        content=ft.Column([
            # Header section
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Column([
                            ft.Text("Invoices", size=32, weight="bold", color="#1F2937"),
                            ft.Text("Manage and track all your generated invoices", size=16, color="#6B7280")
                        ], spacing=8),
                        ft.ElevatedButton(
                            content=ft.Row([
                                ft.Icon("add", color="white"),
                                ft.Text("Create Invoice", size=14, weight="w600")
                            ], spacing=8),
                            bgcolor="#1565C0",
                            color="white",
                            height=48,
                            style=ft.ButtonStyle(
                                text_style=ft.TextStyle(size=14, weight="w600")
                            ),
                            on_click=lambda e: page.go("/manual")
                        )
                    ], alignment="spaceBetween"),
                    
                    ft.Container(height=24),
                    
                    # Search and filters
                    ft.Row([
                        search_field,
                        ft.Container(expand=True),
                        ft.OutlinedButton(
                            content=ft.Row([
                                ft.Icon("download", size=16),
                                ft.Text("Export All", size=14, weight="w500")
                            ], spacing=8),
                            height=48,
                            style=ft.ButtonStyle(
                                color={"": "#1565C0"}
                            )
                        )
                    ], alignment="spaceBetween"),
                    
                    ft.Container(height=16),
                    
                    # Filter buttons
                    ft.Row([
                        ft.Text("Filter by status:", size=14, weight="w500", color="#374151"),
                        ft.Container(width=12),
                        filter_row
                    ], alignment="start")
                ], spacing=0),
                padding=32,
                bgcolor="white",
                border_radius=16,
                border=ft.border.all(1, "#E5E7EB")
            ),
            
            ft.Container(height=24),
            
            # Invoice list
            ft.Container(
                content=ft.Column([
                    invoice_list
                ], scroll=ft.ScrollMode.AUTO),
                bgcolor="white",
                border_radius=16,
                border=ft.border.all(1, "#E5E7EB"),
                expand=True
            )
        ], spacing=0),
        padding=40,
        bgcolor="#F8FAFC",
        expand=True
    ) 