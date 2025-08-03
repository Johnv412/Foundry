#!/usr/bin/env python3
"""
🚀 Foundry OS Dashboard Launcher
One-click dashboard startup with environment setup
"""

import subprocess
import sys
import os
from pathlib import Path

def check_and_install_requirements():
    """Check and install required packages"""
    print("🔍 Checking requirements...")
    
    required_packages = [
        'streamlit>=1.28.0',
        'plotly>=5.17.0', 
        'pandas>=2.0.0'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        package_name = package.split('>')[0].split('=')[0]
        try:
            __import__(package_name)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"📦 Installing {len(missing_packages)} missing packages...")
        for package in missing_packages:
            try:
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', '--user', package
                ])
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
                print("💡 Try running: pip3 install --user streamlit plotly pandas")
                return False
    else:
        print("✅ All requirements satisfied!")
    
    return True

def launch_dashboard():
    """Launch the Streamlit dashboard"""
    dashboard_file = Path(__file__).parent / 'dashboard.py'
    
    if not dashboard_file.exists():
        print("❌ Dashboard file not found!")
        return False
    
    print("🚀 Launching AI Empire Dashboard...")
    print("🌐 Opening in your default browser...")
    print("🛑 Press Ctrl+C to stop the dashboard")
    print("=" * 50)
    
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', str(dashboard_file),
            '--theme.base', 'light',
            '--theme.primaryColor', '#3b82f6',
            '--server.headless', 'false'
        ])
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except FileNotFoundError:
        print("❌ Streamlit not found. Install with: pip3 install --user streamlit")
        return False
    
    return True

def main():
    print("🏭 FOUNDRY OS DASHBOARD LAUNCHER")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path('foundry_v11.py').exists():
        print("❌ Please run this from the foundry-os directory")
        print("💡 cd ~/Desktop/seoeasyWP/foundry-os")
        return
    
    # Install requirements
    if not check_and_install_requirements():
        return
    
    # Launch dashboard
    launch_dashboard()

if __name__ == '__main__':
    main()