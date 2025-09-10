import flet as ft
import asyncio
import platform
import warnings
from pages.dashboard import dashboard_view
from pages.invoices import invoices_view
from pages.settings import settings_view
from pages.manual_maker import manual_maker_view
from pages.audit_log import audit_log_view

# Suppress asyncio warnings on Windows
if platform.system() == 'Windows':
    warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*Event loop is closed.*")
    warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*coroutine.*was never awaited.*")

def main(page: ft.Page):
    # Configure the page
    page.title = "LedgerFlow"
    page.window_width = 1280
    page.window_height = 800
    page.window_maximizable = True
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    
    # Track current navigation state
    current_route = "/"
    
    # Flag to track if shutdown is in progress
    is_shutting_down = False
    
    # Store the event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    def route_change(route):
        nonlocal current_route
        if not is_shutting_down:
            current_route = route
            update_nav_highlight(current_route)
            content_area.content = get_page_content()
            page.update()

    # Content container that will be updated
    content_area = ft.Container(
        content=dashboard_view(page),  # Pass page to default view
        expand=True,
        bgcolor="#F8FAFC",
        padding=20
    )

    def update_nav_highlight(selected_route: str):
        for btn in [dashboard_btn, invoices_btn, manual_maker_btn, audit_btn, settings_btn]:
            if btn.data == selected_route:
                btn.bgcolor = "#E8EDF9"
                btn.content.controls[0].color = "#1565C0"
                btn.content.controls[1].color = "#1565C0"
            else:
                btn.bgcolor = None
                btn.content.controls[0].color = "#64748B"
                btn.content.controls[1].color = "#64748B"
        page.update()

    def switch_view(view_index: int):
        # Update the content based on selection
        views = {
            0: lambda: dashboard_view(page),
            1: lambda: invoices_view(page),
            2: lambda: manual_maker_view(page),
            3: lambda: audit_log_view(page),
            4: lambda: settings_view(page)
        }
        content_area.content = views[view_index]()
        update_nav_highlight(view_index)
        page.update()

    # Navigation bar at the top
    nav_bar = ft.Container(
        content=ft.Row(
            [
                ft.Text("LedgerFlow", size=24, weight="bold"),
                ft.Container(
                    content=ft.CircleAvatar(
                        content=ft.Text("JD"),
                        bgcolor="#1565C0",
                        color="white",
                    ),
                    margin=ft.margin.only(right=20)
                )
            ],
            alignment="spaceBetween"
        ),
        padding=20,
        bgcolor="white",
        border=ft.border.only(bottom=ft.BorderSide(1, "#E0E0E0"))
    )

    # Navigation buttons
    def nav_button(text: str, icon: str, view_index: int):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(name=icon, color="#64748B"),
                    ft.Text(text, color="#64748B", size=16, weight="w500")
                ],
                spacing=15
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            border_radius=8,
            data=text,
            on_click=lambda _: switch_view(view_index)
        )

    # Create navigation buttons
    dashboard_btn = nav_button("Dashboard", "dashboard", 0)
    invoices_btn = nav_button("Invoices", "description", 1)
    manual_maker_btn = nav_button("Create Invoice", "add_circle", 2)
    audit_btn = nav_button("Audit Log", "verified_user", 3)
    settings_btn = nav_button("Settings", "settings", 4)

    # Highlight dashboard by default
    dashboard_btn.bgcolor = "#E8EDF9"
    dashboard_btn.content.controls[0].color = "#1565C0"
    dashboard_btn.content.controls[1].color = "#1565C0"

    # Sidebar container
    sidebar = ft.Container(
        content=ft.Column(
            [
                ft.Container(height=20),  # Spacing after nav_bar
                dashboard_btn,
                invoices_btn,
                manual_maker_btn,
                audit_btn,
                settings_btn
            ],
            spacing=5
        ),
        width=250,
        bgcolor="white",
        border=ft.border.only(right=ft.BorderSide(1, "#E0E0E0"))
    )

    # Page content
    def get_page_content():
        if current_route == "/":
            return dashboard_view(page)
        elif current_route == "/invoices":
            return invoices_view(page)
        elif current_route == "/manual":
            return manual_maker_view(page)
        elif current_route == "/audit":
            return audit_log_view(page)
        else:  # settings
            return settings_view(page)

    # Main layout structure
    page.add(
        nav_bar,
        ft.Row(
            [
                sidebar,
                content_area
            ],
            expand=True,
            spacing=0
        )
    )

    # Set up routing
    page.on_route_change = route_change
    page.go(page.route)
    
    # Handle page close event for proper cleanup
    def on_disconnect(e):
        nonlocal is_shutting_down
        try:
            is_shutting_down = True
            print("Page disconnected - cleaning up...")
            # Cancel any pending tasks safely
            try:
                current_loop = asyncio.get_running_loop()
                pending = [task for task in asyncio.all_tasks(current_loop) if not task.done()]
                for task in pending:
                    task.cancel()
                print(f"Cancelled {len(pending)} pending tasks")
            except RuntimeError:
                # No running loop, nothing to clean up
                pass
        except Exception as ex:
            print(f"Cleanup error (non-critical): {ex}")

    page.on_disconnect = on_disconnect

if __name__ == "__main__":
    import sys
    
    try:
        # Try advanced options first
        ft.app(
            target=main,
            view=ft.AppView.FLET_APP,
            port=0  # Use random available port
        )
    except KeyboardInterrupt:
        print("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Application error: {e}")
        # Try fallback to basic app
        try:
            print("Trying basic app mode...")
            ft.app(target=main)
        except Exception as fallback_error:
            print(f"Fallback error: {fallback_error}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    finally:
        # Clean up any remaining asyncio tasks
        try:
            loop = asyncio.get_event_loop()
            if loop and not loop.is_closed():
                pending_tasks = asyncio.all_tasks(loop)
                if pending_tasks:
                    print(f"Cancelling {len(pending_tasks)} pending tasks...")
                    for task in pending_tasks:
                        if not task.done():
                            task.cancel()
                    # Give tasks a chance to complete
                    try:
                        loop.run_until_complete(asyncio.gather(*pending_tasks, return_exceptions=True))
                    except Exception:
                        pass
                loop.close()
        except Exception as ex:
            print(f"Final cleanup error (non-critical): {ex}")
        
        print("Application shutdown complete.")
