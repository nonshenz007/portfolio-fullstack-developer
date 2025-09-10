"""
LedgerFlow Application Launcher
This script helps avoid asyncio event loop issues on Windows
"""
import sys
import asyncio
import platform

def setup_windows_asyncio():
    """Set up asyncio properly for Windows"""
    if platform.system() == 'Windows':
        # Use the Windows-specific event loop policy
        if hasattr(asyncio, 'WindowsProactorEventLoopPolicy'):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        elif hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        # Suppress warnings about event loop closure
        import warnings
        warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*coroutine.*was never awaited.*")
        warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*Event loop is closed.*")

def main():
    """Main application entry point"""
    try:
        setup_windows_asyncio()
        
        # Import and run the main app
        from main import main as app_main
        import flet as ft
        
        print("Starting LedgerFlow...")
        ft.app(target=app_main, view=ft.AppView.FLET_APP)
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to close...")
    finally:
        # Final cleanup
        try:
            loop = asyncio.get_event_loop()
            if not loop.is_closed():
                loop.close()
        except Exception:
            pass
        print("Application closed.")

if __name__ == "__main__":
    main() 