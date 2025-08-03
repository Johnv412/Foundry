#!/usr/bin/env python3
"""
Foundry OS v1.1 - The AI Empire Command Center
PLUG-AND-PLAY PROJECT SYSTEM with Manifest-Driven Architecture
"""

import os
import sys
import click
import yaml
import json
import jsonschema
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

# Version
__version__ = "1.1.0"

# Determine hub directory
HUB_DIR = Path.home() / "ai-empire-hub"
CONFIG_FILE = HUB_DIR / "config" / "foundry.yaml"
PROJECTS_DIR = HUB_DIR / "projects"
SCHEMA_FILE = HUB_DIR / "schemas" / "project_manifest.json"

class FoundryOS:
    """Main Foundry OS v1.1 controller with Manifest System"""
    
    def __init__(self):
        self.hub_dir = HUB_DIR
        self.projects_dir = PROJECTS_DIR
        self.config = self.load_config()
        self.schema = self.load_schema()
        
    def load_config(self) -> Dict:
        """Load configuration from YAML"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return yaml.safe_load(f)
        return self.get_default_config()
    
    def load_schema(self) -> Dict:
        """Load project manifest schema"""
        if SCHEMA_FILE.exists():
            with open(SCHEMA_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def get_default_config(self) -> Dict:
        """Return default configuration"""
        return {
            'version': __version__,
            'hub_directory': str(self.hub_dir),
            'manifest_system': True,
            'agents': {},
            'templates': {
                'SaaS_Launch_Playbook': {
                    'name': 'SaaS Launch Team',
                    'agents': ['architect_specialist', 'app_factory_specialist', 'devops_specialist', 'data_intelligence_agent'],
                    'default_stack': 'react-node'
                },
                'restaurant_bot': {
                    'name': 'Restaurant Bot Team',
                    'agents': ['api_integration_master', 'app_factory_specialist', 'qa_specialist'],
                    'default_stack': 'python-fastapi'
                },
                'marketplace': {
                    'name': 'Marketplace Team',
                    'agents': ['architect_specialist', 'api_integration_master', 'app_factory_specialist', 'devops_specialist'],
                    'default_stack': 'nextjs-postgres'
                }
            },
            'learning': {
                'metrics_threshold': 0.25,
                'auto_save_patterns': False
            }
        }
    
    def ensure_directories(self):
        """Ensure all required directories exist"""
        dirs = [
            'agents', 'projects', 'templates', 
            'shared-context', 'logs', 'config',
            'memory-bank', 'metrics', 'schemas'
        ]
        for dir_name in dirs:
            (self.hub_dir / dir_name).mkdir(parents=True, exist_ok=True)
    
    def discover_projects(self) -> List[Dict]:
        """Discover all projects by reading manifest files"""
        projects = []
        
        if not self.projects_dir.exists():
            return projects
        
        for manifest_file in self.projects_dir.glob("*.json"):
            try:
                with open(manifest_file, 'r') as f:
                    project_data = json.load(f)
                
                # Validate against schema
                if self.schema:
                    jsonschema.validate(project_data, self.schema)
                
                # Add metadata
                project_data['_manifest_file'] = str(manifest_file)
                project_data['_last_modified'] = datetime.fromtimestamp(
                    manifest_file.stat().st_mtime
                ).isoformat()
                
                projects.append(project_data)
                
            except json.JSONDecodeError as e:
                self.log(f"ERROR: Invalid JSON in {manifest_file}: {e}")
            except jsonschema.ValidationError as e:
                self.log(f"ERROR: Invalid manifest schema in {manifest_file}: {e}")
            except Exception as e:
                self.log(f"ERROR: Failed to load {manifest_file}: {e}")
        
        return sorted(projects, key=lambda x: x.get('projectName', ''))
    
    def find_project(self, project_name: str) -> Optional[Dict]:
        """Find a project by name"""
        projects = self.discover_projects()
        for project in projects:
            if project.get('projectName', '').lower() == project_name.lower():
                return project
        return None
    
    def create_project_from_manifest(self, manifest_path: str) -> Dict:
        """Create a new project from a manifest file"""
        manifest_file = Path(manifest_path)
        
        if not manifest_file.exists():
            raise click.ClickException(f"Manifest file not found: {manifest_path}")
        
        # Load and validate manifest
        with open(manifest_file, 'r') as f:
            project_data = json.load(f)
        
        if self.schema:
            jsonschema.validate(project_data, self.schema)
        
        # Copy manifest to projects directory
        project_name = project_data.get('projectName', 'unknown')
        project_id = project_name.lower().replace(' ', '_')
        target_file = self.projects_dir / f"{project_id}.json"
        
        if target_file.exists():
            raise click.ClickException(f"Project '{project_name}' already exists")
        
        # Copy manifest file
        with open(target_file, 'w') as f:
            json.dump(project_data, f, indent=2)
        
        self.log(f"Created project '{project_name}' from manifest")
        return project_data
    
    def assign_task(self, task: str, project_name: str, agent: str) -> Dict:
        """Assign a task to an agent for a specific project"""
        project = self.find_project(project_name)
        
        if not project:
            raise click.ClickException(f"Project '{project_name}' not found")
        
        if agent not in self.config.get('agents', {}):
            # Check if agent is in project team
            if agent not in project.get('team', []):
                click.echo(f"⚠️  Warning: Agent '{agent}' not registered or in project team")
        
        # Create task assignment
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        assignment = {
            'id': task_id,
            'task': task,
            'project': project_name,
            'agent': agent,
            'status': 'assigned',
            'created_at': datetime.now().isoformat(),
            'completed_at': None,
            'result': None
        }
        
        # Save to shared context
        shared_file = self.hub_dir / 'shared-context' / f'{project_name.lower().replace(" ", "_")}_{task_id}.json'
        shared_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(shared_file, 'w') as f:
            json.dump(assignment, f, indent=2)
        
        self.log(f"Assigned task '{task}' to {agent} for project {project_name}")
        return assignment
    
    def get_empire_status(self) -> Dict:
        """Get comprehensive status of the entire AI Empire"""
        projects = self.discover_projects()
        
        # Calculate empire metrics
        total_projects = len(projects)
        active_projects = len([p for p in projects if p.get('status') not in ['archived', 'completed']])
        
        # Revenue calculation (if available)
        total_revenue = 0
        revenue_projects = 0
        for project in projects:
            metrics = project.get('metrics', {})
            revenue_str = metrics.get('revenue', '$0')
            if revenue_str and revenue_str.startswith('$'):
                try:
                    revenue = float(revenue_str.replace('$', '').replace(',', ''))
                    total_revenue += revenue
                    revenue_projects += 1
                except ValueError:
                    pass
        
        # Status distribution
        status_counts = {}
        for project in projects:
            status = project.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Team utilization
        agent_workload = {}
        for project in projects:
            if project.get('status') not in ['archived', 'completed']:
                for agent in project.get('team', []):
                    agent_workload[agent] = agent_workload.get(agent, 0) + 1
        
        return {
            'total_projects': total_projects,
            'active_projects': active_projects,
            'total_revenue': total_revenue,
            'revenue_projects': revenue_projects,
            'status_distribution': status_counts,
            'agent_workload': agent_workload,
            'projects': projects
        }
    
    def log(self, message: str):
        """Log a message to the system log"""
        log_file = self.hub_dir / 'logs' / f"foundry_{datetime.now().strftime('%Y%m%d')}.log"
        log_file.parent.mkdir(exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")

# CLI Commands
@click.group()
@click.pass_context
def cli(ctx):
    """Foundry OS v1.1 - The AI Empire Command Center with Manifest System"""
    ctx.obj = FoundryOS()
    ctx.obj.ensure_directories()

@cli.command()
def version():
    """Show Foundry OS version"""
    click.echo(f"🏭 Foundry OS v{__version__}")
    click.echo("The AI Empire Command Center - PLUG-AND-PLAY Edition")

@cli.command()
@click.option('--manifest', '-m', help='Path to project manifest file')
@click.pass_obj
def new(foundry: FoundryOS, manifest: Optional[str]):
    """Create a new project from a manifest file"""
    if not manifest:
        click.echo("❌ Error: --manifest parameter is required", err=True)
        click.echo("Example: foundry new --manifest=./my_project.json")
        return
    
    try:
        project = foundry.create_project_from_manifest(manifest)
        click.echo(f"✅ Created project '{project['projectName']}'")
        click.echo(f"📋 Type: {project['projectType']}")
        click.echo(f"🎯 Status: {project['status']}")
        
        if project.get('team'):
            click.echo(f"👥 Team: {', '.join(project['team'])}")
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)

@cli.command()
@click.argument('task')
@click.option('--project', '-p', required=True, help='Project name')
@click.option('--agent', '-a', required=True, help='Agent to assign')
@click.pass_obj
def assign(foundry: FoundryOS, task: str, project: str, agent: str):
    """Assign a task to an agent"""
    try:
        assignment = foundry.assign_task(task, project, agent)
        click.echo(f"✅ Task assigned [{assignment['id']}]")
        click.echo(f"📋 Task: {task}")
        click.echo(f"👤 Agent: {agent}")
        click.echo(f"📁 Project: {project}")
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)

@cli.command()
@click.option('--all', is_flag=True, help='Show detailed project information')
@click.option('--summary', is_flag=True, help='Show empire summary only')
@click.pass_obj
def status(foundry: FoundryOS, all: bool, summary: bool):
    """Show AI Empire status and project overview"""
    empire_status = foundry.get_empire_status()
    
    # Always show empire summary
    click.echo("\n🏭 AI EMPIRE STATUS REPORT")
    click.echo("=" * 60)
    click.echo(f"📊 Total Projects: {empire_status['total_projects']}")
    click.echo(f"🔄 Active Projects: {empire_status['active_projects']}")
    
    if empire_status['revenue_projects'] > 0:
        click.echo(f"💰 Total Revenue: ${empire_status['total_revenue']:,.2f}")
    
    # Status distribution
    if empire_status['status_distribution']:
        click.echo("\n📈 Project Status Distribution:")
        for status, count in empire_status['status_distribution'].items():
            status_emoji = {
                'planning': '📋', 'development': '🔨', 'testing': '🧪',
                'production': '🚀', 'maintenance': '🔧', 'archived': '📦'
            }.get(status, '❓')
            click.echo(f"   {status_emoji} {status.title()}: {count}")
    
    # Agent workload
    if empire_status['agent_workload']:
        click.echo("\n👥 Agent Workload:")
        for agent, count in sorted(empire_status['agent_workload'].items()):
            click.echo(f"   🤖 {agent}: {count} project(s)")
    
    if summary:
        return
    
    # Project details
    projects = empire_status['projects']
    if not projects:
        click.echo("\nNo projects found. Create your first project with:")
        click.echo("foundry new --manifest=./project.json")
        return
    
    click.echo(f"\n📋 PROJECT DETAILS ({len(projects)} total)")
    click.echo("=" * 60)
    
    for project in projects:
        status_emoji = {
            'planning': '📋', 'development': '🔨', 'testing': '🧪',
            'production': '🚀', 'maintenance': '🔧', 'archived': '📦'
        }.get(project.get('status'), '❓')
        
        click.echo(f"\n{status_emoji} {project['projectName']}")
        click.echo(f"   Type: {project.get('projectType', 'Unknown')}")
        click.echo(f"   Status: {project.get('status', 'Unknown')}")
        click.echo(f"   Lead: {project.get('leadStrategist', 'Unknown')}")
        
        if project.get('liveUrl'):
            click.echo(f"   🌐 Live: {project['liveUrl']}")
        
        if project.get('description'):
            click.echo(f"   📝 {project['description']}")
        
        # Show metrics if available
        metrics = project.get('metrics', {})
        if metrics.get('revenue'):
            click.echo(f"   💰 Revenue: {metrics['revenue']}")
        if metrics.get('users'):
            click.echo(f"   👥 Users: {metrics['users']}")
        
        # Show active tasks if requested
        if all and project.get('tasks', {}).get('active'):
            active_tasks = project['tasks']['active']
            click.echo(f"   📋 Active Tasks ({len(active_tasks)}):")
            for task in active_tasks[:3]:  # Show max 3 tasks
                priority_emoji = {'high': '🔥', 'medium': '⚡', 'low': '📌'}.get(task.get('priority'), '📌')
                click.echo(f"      {priority_emoji} {task['description']} → {task['assignedTo']}")

@cli.command()
@click.pass_obj
def projects(foundry: FoundryOS):
    """List all discovered projects"""
    projects = foundry.discover_projects()
    
    if not projects:
        click.echo("No projects found.")
        click.echo("Create a project manifest file in the projects directory.")
        return
    
    click.echo(f"\n📁 DISCOVERED PROJECTS ({len(projects)})")
    click.echo("=" * 50)
    
    for project in projects:
        status_emoji = {
            'planning': '📋', 'development': '🔨', 'testing': '🧪',
            'production': '🚀', 'maintenance': '🔧', 'archived': '📦'
        }.get(project.get('status'), '❓')
        
        click.echo(f"{status_emoji} {project['projectName']} ({project.get('projectType', 'Unknown')})")

@cli.command()
@click.pass_obj
def init(foundry: FoundryOS):
    """Initialize Foundry OS v1.1 with Manifest System"""
    click.echo("🏗️  Initializing Foundry OS v1.1...")
    click.echo("📋 Enabling PLUG-AND-PLAY Project System...")
    
    # Ensure all directories exist
    foundry.ensure_directories()
    
    # Create initial config
    if not CONFIG_FILE.exists():
        config = foundry.get_default_config()
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
    
    # Create welcome file
    welcome_file = foundry.hub_dir / 'README.md'
    if not welcome_file.exists():
        welcome_content = """# Foundry OS v1.1 - AI Empire Hub
## 🔌 PLUG-AND-PLAY PROJECT SYSTEM

Welcome to the next evolution of your AI Empire Command Center!

## 🚀 Quick Start

1. **Create a project manifest** (JSON file):
   ```json
   {
     "projectName": "My Amazing Startup",
     "projectType": "SaaS_Launch_Playbook",
     "leadStrategist": "Claude",
     "leadArchitect": "PromptDEV",
     "status": "planning"
   }
   ```

2. **Plug it in**:
   ```
   foundry new --manifest=./my_project.json
   ```

3. **Check your empire**:
   ```
   foundry status
   ```

## 📋 Manifest System

Projects are now defined by simple JSON files in the `/projects` directory.
Drop in a manifest, and Foundry OS automatically discovers and manages it!

## 🎯 Example Projects Included

- **HugemouthSEO**: Production SaaS platform
- **AI Pizza Pro**: Restaurant bot in development  
- **SEOEasy Directory**: Marketplace platform

Run `foundry status` to see your empire at a glance!
"""
        with open(welcome_file, 'w') as f:
            f.write(welcome_content)
    
    click.echo(f"✅ Foundry OS v1.1 initialized at: {foundry.hub_dir}")
    click.echo(f"📁 Project manifests directory: {foundry.projects_dir}")
    click.echo("\n🎯 Next steps:")
    click.echo("1. Run 'foundry status' to see your empire")
    click.echo("2. Create a new project manifest and use 'foundry new --manifest=file.json'")
    click.echo("3. Run 'foundry projects' to see all discovered projects")

if __name__ == '__main__':
    cli()