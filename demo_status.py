#!/usr/bin/env python3
"""
Demo script showing Foundry OS v1.1 manifest-driven project discovery
"""

import json
import os
from pathlib import Path

def discover_projects():
    """Discover projects from manifest files"""
    projects_dir = Path("ai-empire-hub/projects")
    projects = []
    
    if not projects_dir.exists():
        return projects
    
    for manifest_file in projects_dir.glob("*.json"):
        try:
            with open(manifest_file, 'r') as f:
                project_data = json.load(f)
            projects.append(project_data)
        except Exception as e:
            print(f"Error loading {manifest_file}: {e}")
    
    return projects

def show_empire_status():
    """Show comprehensive empire status"""
    print("🏭 FOUNDRY OS v1.1 - AI EMPIRE STATUS")
    print("=" * 50)
    print("📋 PLUG-AND-PLAY PROJECT SYSTEM ACTIVE")
    print()
    
    projects = discover_projects()
    
    if not projects:
        print("No projects found. Create manifest files in projects/ directory.")
        return
    
    # Calculate metrics
    total_projects = len(projects)
    active_projects = len([p for p in projects if p.get('status') not in ['archived']])
    
    # Revenue calculation
    total_revenue = 0
    for project in projects:
        metrics = project.get('metrics', {})
        revenue_str = metrics.get('revenue', '$0')
        if revenue_str and revenue_str.startswith('$'):
            try:
                revenue = float(revenue_str.replace('$', '').replace(',', ''))
                total_revenue += revenue
            except ValueError:
                pass
    
    print(f"📊 Total Projects: {total_projects}")
    print(f"🔄 Active Projects: {active_projects}")
    print(f"💰 Total Revenue: ${total_revenue:,.2f}")
    print()
    
    # Show project details
    print("📋 PROJECT PORTFOLIO:")
    print("-" * 40)
    
    for project in projects:
        status_emoji = {
            'planning': '📋', 'development': '🔨', 'testing': '🧪',
            'production': '🚀', 'maintenance': '🔧', 'archived': '📦'
        }.get(project.get('status'), '❓')
        
        print(f"{status_emoji} {project.get('projectName', project.get('name', 'Unknown Project'))}")
        print(f"   Type: {project.get('projectType', 'Unknown')}")
        print(f"   Status: {project.get('status', 'Unknown')}")
        print(f"   Lead: {project.get('leadStrategist', 'Unknown')}")
        
        if project.get('liveUrl'):
            print(f"   🌐 {project['liveUrl']}")
        
        # Show metrics
        metrics = project.get('metrics', {})
        if metrics.get('revenue'):
            print(f"   💰 Revenue: {metrics['revenue']}")
        if metrics.get('users'):
            print(f"   👥 Users: {metrics['users']}")
        
        # Show active tasks
        active_tasks = project.get('tasks', {}).get('active', [])
        if active_tasks:
            print(f"   📋 Active Tasks ({len(active_tasks)}):")
            for task in active_tasks[:2]:  # Show first 2
                priority_emoji = {
                    'high': '🔥', 'medium': '⚡', 'low': '📌'
                }.get(task.get('priority'), '📌')
                print(f"      {priority_emoji} {task['description']} → {task['assignedTo']}")
        
        print()
    
    print("✅ Empire status complete!")
    print()
    print("🎯 Next steps:")
    print("1. Install dependencies: pip3 install click pyyaml jsonschema")
    print("2. Run: python3 foundry_v11.py status")
    print("3. Create new projects by dropping manifest files in projects/")

if __name__ == '__main__':
    show_empire_status()