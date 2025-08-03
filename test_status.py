#!/usr/bin/env python3
"""
Test script to demonstrate Foundry OS v1.1 status command
Shows the manifest-driven project discovery system
"""

import sys
import os

# Add the foundry module to path
sys.path.insert(0, '/Users/macbook/Desktop/seoeasyWP/foundry-os')

# Import and test
from foundry_v11 import FoundryOS

def test_status():
    """Test the status functionality"""
    print("🧪 Testing Foundry OS v1.1 Status Command")
    print("=" * 50)
    
    # Initialize Foundry OS
    foundry = FoundryOS()
    foundry.ensure_directories()
    
    # Get empire status
    status = foundry.get_empire_status()
    
    print(f"📊 Projects discovered: {status['total_projects']}")
    print(f"🔄 Active projects: {status['active_projects']}")
    print(f"💰 Total revenue: ${status['total_revenue']:,.2f}")
    
    print("\n📋 Project Details:")
    for project in status['projects']:
        print(f"  • {project['projectName']} ({project['status']})")
        print(f"    Type: {project['projectType']}")
        print(f"    Lead: {project['leadStrategist']}")
        
        if project.get('liveUrl'):
            print(f"    URL: {project['liveUrl']}")
        
        # Show active tasks
        active_tasks = project.get('tasks', {}).get('active', [])
        if active_tasks:
            print(f"    Active Tasks: {len(active_tasks)}")
            for task in active_tasks[:2]:  # Show first 2 tasks
                print(f"      - {task['description']} → {task['assignedTo']}")
        print()
    
    print("✅ Status test completed!")

if __name__ == '__main__':
    test_status()