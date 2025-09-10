# This file will contain the UI for the audit log page. 

import flet as ft
from datetime import datetime, timedelta
import hashlib
import json
import random

def audit_log_view(page: ft.Page):
    # Sample audit data for demo - in real app this would come from VeriChain™
    sample_audit_entries = [
        {
            "timestamp": "2024-01-20 10:30:15",
            "action": "Invoice Generated",
            "invoice_id": "INV-45127",
            "user": "System",
            "hash": "a3b8c9d2e4f6789012345abcdef67890",
            "previous_hash": "b2c7d8e3f5789012345abcdef67890a1",
            "verified": True,
            "details": "Batch generation: 25 invoices, Revenue: ₹75,000"
        },
        {
            "timestamp": "2024-01-20 09:45:22",
            "action": "Manual Invoice Created",
            "invoice_id": "INV-45126",
            "user": "Admin",
            "hash": "b2c7d8e3f5789012345abcdef67890a1",
            "previous_hash": "c1d6e7f2489012345abcdef67890b2c3",
            "verified": True,
            "details": "Customer: Priya Verma, Amount: ₹4,250.25"
        },
        {
            "timestamp": "2024-01-20 09:15:08",
            "action": "Export Completed",
            "invoice_id": "BATCH-001",
            "user": "System", 
            "hash": "c1d6e7f2489012345abcdef67890b2c3",
            "previous_hash": "d0e5f6c1378012345abcdef67890c1d4",
            "verified": True,
            "details": "PDF export: 18 invoices, GST template"
        },
        {
            "timestamp": "2024-01-19 16:20:45",
            "action": "Settings Modified",
            "invoice_id": "CONFIG-001",
            "user": "Admin",
            "hash": "d0e5f6c1378012345abcdef67890c1d4",
            "previous_hash": "e9f4c5b0267012345abcdef67890d0e5",
            "verified": True,
            "details": "Updated business style: Medical → Grocery"
        },
        {
            "timestamp": "2024-01-19 14:12:33",
            "action": "Invoice Generated",
            "invoice_id": "INV-45125",
            "user": "System",
            "hash": "e9f4c5b0267012345abcdef67890d0e5",
            "previous_hash": "f8c3b4a9156012345abcdef67890e9f4",
            "verified": False,  # Simulate a verification failure
            "details": "VAT template: Customer Omar Hassan"
        }
    ]
    
    # State variables
    filtered_entries = sample_audit_entries.copy()
    selected_filter = "All"
    search_query = ""
    verification_status = "All verified" if all(entry["verified"] for entry in sample_audit_entries) else "Issues detected"
    
    def get_action_color(action):
        colors = {
            "Invoice Generated": "#059669",
            "Manual Invoice Created": "#1565C0",
            "Export Completed": "#7C3AED",
            "Settings Modified": "#F59E0B",
            "System Error": "#DC2626"
        }
        return colors.get(action, "#6B7280")
    
    def get_action_icon(action):
        icons = {
            "Invoice Generated": "auto_awesome",
            "Manual Invoice Created": "edit",
            "Export Completed": "download",
            "Settings Modified": "settings",
            "System Error": "error"
        }
        return icons.get(action, "info")
    
    def filter_entries(filter_type):
        def handler(e):
            nonlocal selected_filter, filtered_entries
            selected_filter = filter_type
            apply_filters()
            update_filter_buttons()
            update_audit_table()
        return handler
    
    def search_entries(e):
        nonlocal search_query, filtered_entries
        search_query = e.control.value.lower()
        apply_filters()
        update_audit_table()
    
    def apply_filters():
        nonlocal filtered_entries
        filtered_entries = sample_audit_entries.copy()
        
        # Apply verification filter
        if selected_filter == "Verified":
            filtered_entries = [entry for entry in filtered_entries if entry["verified"]]
        elif selected_filter == "Issues":
            filtered_entries = [entry for entry in filtered_entries if not entry["verified"]]
        
        # Apply search filter
        if search_query:
            filtered_entries = [
                entry for entry in filtered_entries 
                if (search_query in entry["action"].lower() or 
                    search_query in entry["invoice_id"].lower() or
                    search_query in entry["details"].lower())
            ]
    
    def verify_hash_chain(e):
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Running hash chain verification...", color="white"),
            bgcolor="#1565C0"
        )
        page.snack_bar.open = True
        page.update()
        
        # Simulate verification process
        import time
        time.sleep(1)
        
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Hash chain verification completed successfully!", color="white"),
            bgcolor="#10B981"
        )
        page.snack_bar.open = True
        page.update()
    
    def export_audit_log(e):
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Exporting audit log to CSV...", color="white"),
            bgcolor="#1565C0"
        )
        page.snack_bar.open = True
        page.update()
    
    def view_entry_details(entry):
        def handler(e):
            # Create detailed view dialog
            details_content = ft.Column([
                ft.Text("Audit Entry Details", size=20, weight="bold", color="#1F2937"),
                ft.Container(height=16),
                
                ft.Row([
                    ft.Text("Timestamp:", size=14, weight="w600", color="#374151"),
                    ft.Text(entry["timestamp"], size=14, color="#6B7280")
                ], alignment="spaceBetween"),
                
                ft.Row([
                    ft.Text("Action:", size=14, weight="w600", color="#374151"),
                    ft.Container(
                        content=ft.Text(entry["action"], size=12, weight="w500", color="white"),
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        bgcolor=get_action_color(entry["action"]),
                        border_radius=12
                    )
                ], alignment="spaceBetween"),
                
                ft.Row([
                    ft.Text("Invoice ID:", size=14, weight="w600", color="#374151"),
                    ft.Text(entry["invoice_id"], size=14, color="#6B7280")
                ], alignment="spaceBetween"),
                
                ft.Row([
                    ft.Text("User:", size=14, weight="w600", color="#374151"),
                    ft.Text(entry["user"], size=14, color="#6B7280")
                ], alignment="spaceBetween"),
                
                ft.Container(height=16),
                ft.Divider(color="#E5E7EB"),
                ft.Container(height=16),
                
                ft.Text("Hash Chain Details", size=16, weight="bold", color="#374151"),
                ft.Container(height=12),
                
                ft.Column([
                    ft.Text("Current Hash:", size=12, weight="w600", color="#6B7280"),
                    ft.Container(
                        content=ft.Text(entry["hash"], size=12, color="#1F2937", style=ft.TextStyle(font_family="monospace")),
                        padding=8,
                        bgcolor="#F3F4F6",
                        border_radius=4
                    )
                ]),
                
                ft.Container(height=12),
                
                ft.Column([
                    ft.Text("Previous Hash:", size=12, weight="w600", color="#6B7280"),
                    ft.Container(
                        content=ft.Text(entry["previous_hash"], size=12, color="#1F2937", style=ft.TextStyle(font_family="monospace")),
                        padding=8,
                        bgcolor="#F3F4F6",
                        border_radius=4
                    )
                ]),
                
                ft.Container(height=16),
                
                ft.Row([
                    ft.Text("Verification Status:", size=14, weight="w600", color="#374151"),
                    ft.Row([
                        ft.Icon(
                            "check_circle" if entry["verified"] else "error",
                            color="#10B981" if entry["verified"] else "#DC2626",
                            size=16
                        ),
                        ft.Text(
                            "Verified" if entry["verified"] else "Failed",
                            size=14,
                            color="#10B981" if entry["verified"] else "#DC2626",
                            weight="w600"
                        )
                    ], spacing=4)
                ], alignment="spaceBetween"),
                
                ft.Container(height=16),
                ft.Divider(color="#E5E7EB"),
                ft.Container(height=16),
                
                ft.Text("Details", size=16, weight="bold", color="#374151"),
                ft.Container(height=8),
                ft.Text(entry["details"], size=14, color="#6B7280")
            ], spacing=8)
            
            dialog = ft.AlertDialog(
                title=ft.Text("Audit Entry"),
                content=ft.Container(
                    content=details_content,
                    width=500,
                    height=600
                ),
                actions=[
                    ft.TextButton("Close", on_click=lambda e: close_dialog(dialog))
                ],
                actions_alignment="end"
            )
            
            page.dialog = dialog
            dialog.open = True
            page.update()
        return handler
    
    def close_dialog(dialog):
        dialog.open = False
        page.update()
    
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
            on_click=filter_entries(text)
        )
    
    def update_filter_buttons():
        filter_row.controls.clear()
        
        # Count entries by verification status
        verified_count = sum(1 for entry in sample_audit_entries if entry["verified"])
        issues_count = len(sample_audit_entries) - verified_count
        
        # Add filter buttons
        filter_row.controls.extend([
            create_filter_button("All", len(sample_audit_entries)),
            create_filter_button("Verified", verified_count),
            create_filter_button("Issues", issues_count)
        ])
        page.update()
    
    def create_audit_entry_row(entry):
        return ft.Container(
            content=ft.Row([
                # Timestamp and action
                ft.Column([
                    ft.Row([
                        ft.Icon(
                            get_action_icon(entry["action"]),
                            color=get_action_color(entry["action"]),
                            size=16
                        ),
                        ft.Text(entry["action"], size=14, weight="w600", color="#1F2937")
                    ], spacing=8),
                    ft.Text(entry["timestamp"], size=12, color="#6B7280")
                ], spacing=4, tight=True),
                
                # Invoice ID
                ft.Container(
                    content=ft.Text(entry["invoice_id"], size=14, color="#374151", weight="w500"),
                    width=120
                ),
                
                # User
                ft.Container(
                    content=ft.Text(entry["user"], size=14, color="#6B7280"),
                    width=80
                ),
                
                # Hash (truncated)
                ft.Container(
                    content=ft.Text(
                        f"{entry['hash'][:8]}...",
                        size=12,
                        color="#6B7280",
                        style=ft.TextStyle(font_family="monospace")
                    ),
                    width=100
                ),
                
                # Verification status
                ft.Container(
                    content=ft.Row([
                        ft.Icon(
                            "check_circle" if entry["verified"] else "error",
                            color="#10B981" if entry["verified"] else "#DC2626",
                            size=16
                        ),
                        ft.Text(
                            "Verified" if entry["verified"] else "Failed",
                            size=12,
                            weight="w500",
                            color="#10B981" if entry["verified"] else "#DC2626"
                        )
                    ], spacing=4),
                    width=100,
                    alignment=ft.alignment.center_left
                ),
                
                # Details (truncated)
                ft.Container(
                    content=ft.Text(
                        entry["details"][:40] + "..." if len(entry["details"]) > 40 else entry["details"],
                        size=14,
                        color="#6B7280"
                    ),
                    expand=True
                ),
                
                # View details button
                ft.IconButton(
                    icon="visibility",
                    icon_color="#6B7280",
                    icon_size=18,
                    tooltip="View Details",
                    on_click=view_entry_details(entry)
                )
            ], alignment="center", spacing=16),
            padding=ft.padding.symmetric(horizontal=24, vertical=12),
            bgcolor="white",
            border_radius=8,
            border=ft.border.all(1, "#E5E7EB"),
            margin=ft.margin.only(bottom=8)
        )
    
    def update_audit_table():
        audit_list.controls.clear()
        
        if not filtered_entries:
            # Empty state
            audit_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon("history", size=64, color="#D1D5DB"),
                        ft.Text("No audit entries found", size=18, weight="w600", color="#6B7280"),
                        ft.Text("Try adjusting your filters", size=14, color="#9CA3AF")
                    ], horizontal_alignment="center", spacing=16),
                    padding=64,
                    alignment=ft.alignment.center
                )
            )
        else:
            # Add header row
            audit_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text("Action", size=12, weight="bold", color="#6B7280"),
                        ft.Container(
                            content=ft.Text("Invoice ID", size=12, weight="bold", color="#6B7280"),
                            width=120
                        ),
                        ft.Container(
                            content=ft.Text("User", size=12, weight="bold", color="#6B7280"),
                            width=80
                        ),
                        ft.Container(
                            content=ft.Text("Hash", size=12, weight="bold", color="#6B7280"),
                            width=100
                        ),
                        ft.Container(
                            content=ft.Text("Status", size=12, weight="bold", color="#6B7280"),
                            width=100
                        ),
                        ft.Text("Details", size=12, weight="bold", color="#6B7280"),
                        ft.Container(width=40)  # For actions
                    ], alignment="center", spacing=16),
                    padding=ft.padding.symmetric(horizontal=24, vertical=12),
                    bgcolor="#F9FAFB",
                    border_radius=ft.border_radius.only(top_left=8, top_right=8)
                )
            )
            
            # Add audit entry rows
            for entry in filtered_entries:
                audit_list.controls.append(create_audit_entry_row(entry))
        
        page.update()
    
    # Create UI components
    search_field = ft.TextField(
        hint_text="Search actions, invoice IDs, or details...",
        prefix_icon="search",
        border_color="#D1D5DB",
        focused_border_color="#1565C0",
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        on_change=search_entries,
        width=400
    )
    
    filter_row = ft.Row(spacing=12)
    audit_list = ft.Column(spacing=0)
    
    # Initialize components
    update_filter_buttons()
    update_audit_table()
    
    # VeriChain status indicator
    verichain_status = ft.Container(
        content=ft.Row([
            ft.Icon("verified", color="#10B981", size=20),
            ft.Column([
                ft.Text("VeriChain™ Active", size=14, weight="w600", color="#10B981"),
                ft.Text("Hash chain integrity verified", size=12, color="#6B7280")
            ], spacing=2)
        ], spacing=12),
        padding=16,
        bgcolor="#ECFDF5",
        border_radius=8,
        border=ft.border.all(1, "#D1FAE5")
    )
    
    # Main layout
    return ft.Container(
        content=ft.Column([
            # Header section
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Column([
                            ft.Text("Audit Log", size=32, weight="bold", color="#1F2937"),
                            ft.Text("VeriChain™ hash-chain verification for invoice authenticity", size=16, color="#6B7280")
                        ], spacing=8),
                        ft.Row([
                            ft.OutlinedButton(
                                content=ft.Row([
                                    ft.Icon("verified_user", size=16),
                                    ft.Text("Verify Chain", size=14, weight="w500")
                                ], spacing=8),
                                height=48,
                                style=ft.ButtonStyle(
                                    color={"": "#1565C0"}
                                ),
                                on_click=verify_hash_chain
                            ),
                            ft.Container(width=12),
                            ft.ElevatedButton(
                                content=ft.Row([
                                    ft.Icon("download", color="white"),
                                    ft.Text("Export Log", size=14, weight="w600")
                                ], spacing=8),
                                bgcolor="#1565C0",
                                color="white",
                                height=48,
                                on_click=export_audit_log
                            )
                        ], spacing=0)
                    ], alignment="spaceBetween"),
                    
                    ft.Container(height=24),
                    
                    # VeriChain status
                    verichain_status,
                    
                    ft.Container(height=24),
                    
                    # Search and filters
                    ft.Row([
                        search_field,
                        ft.Container(expand=True),
                        ft.Container(
                            content=ft.Row([
                                ft.Icon("info", color="#1565C0", size=16),
                                ft.Text(f"Total entries: {len(sample_audit_entries)}", size=14, color="#6B7280")
                            ], spacing=8)
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
            
            # Audit log list
            ft.Container(
                content=ft.Column([
                    audit_list
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