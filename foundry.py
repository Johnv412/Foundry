#!/usr/bin/env python3
"""
Foundry OS - The AI Empire Command Center
A unified system for orchestrating AI agents and autonomous business operations.
"""

import os
import sys
import click
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

# Version
__version__ = "1.0.0"

# Determine hub directory
HUB_DIR = Path.home() / "ai-empire-hub"
CONFIG_FILE = HUB_DIR / "config" / "foundry.yaml"

class FoundryOS:
    """Main Foundry OS controller"""
    
    def __init__(self):
        self.hub_dir = HUB_DIR
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Load configuration from YAML"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return yaml.safe_load(f)
        return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Return default configuration"""
        return {
            'version': __version__,
            'hub_directory': str(self.hub_dir),
            'agents': {},
            'templates': {},
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
            'memory-bank', 'metrics'
        ]
        for dir_name in dirs:
            (self.hub_dir / dir_name).mkdir(parents=True, exist_ok=True)
    
    def create_project(self, name: str, template: Optional[str] = None) -> Dict:
        """Create a new project with optional template"""
        project_id = name.lower().replace(' ', '_')
        project_dir = self.hub_dir / 'projects' / project_id
        
        if project_dir.exists():
            raise click.ClickException(f"Project '{name}' already exists")
        
        project_dir.mkdir(parents=True)
        
        # Create project metadata
        metadata = {
            'id': project_id,
            'name': name,
            'template': template,
            'created_at': datetime.now().isoformat(),
            'status': 'initialized',
            'agents': []
        }
        
        # Apply template if specified
        if template and template in self.config.get('templates', {}):
            template_config = self.config['templates'][template]
            metadata['agents'] = template_config.get('agents', [])
            metadata['stack'] = template_config.get('default_stack', 'custom')
            
            # Log template application
            self.log(f"Applied template '{template}' to project '{name}'")
            self.log(f"Assigned agents: {', '.join(metadata['agents'])}")
        
        # Save project metadata
        with open(project_dir / 'project.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Create project subdirectories
        for subdir in ['src', 'docs', 'tests', 'deployments']:
            (project_dir / subdir).mkdir()
        
        return metadata
    
    def assign_agent(self, task: str, project: str, agent: str) -> Dict:
        """Assign a task to an agent for a specific project"""
        project_dir = self.hub_dir / 'projects' / project
        
        if not project_dir.exists():
            raise click.ClickException(f"Project '{project}' not found")
        
        if agent not in self.config.get('agents', {}):
            raise click.ClickException(f"Agent '{agent}' not found")
        
        # Create task assignment
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        assignment = {
            'id': task_id,
            'task': task,
            'project': project,
            'agent': agent,
            'status': 'assigned',
            'created_at': datetime.now().isoformat(),
            'completed_at': None,
            'result': None
        }
        
        # Save to shared context
        shared_file = self.hub_dir / 'shared-context' / f'{project}_{task_id}.json'
        with open(shared_file, 'w') as f:
            json.dump(assignment, f, indent=2)
        
        self.log(f"Assigned task '{task}' to {agent} for project {project}")
        return assignment
    
    def get_status(self, show_all: bool = False) -> List[Dict]:
        """Get status of all projects or active ones"""
        projects = []
        projects_dir = self.hub_dir / 'projects'
        
        if not projects_dir.exists():
            return projects
        
        for project_dir in projects_dir.iterdir():
            if project_dir.is_dir():
                metadata_file = project_dir / 'project.json'
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        
                    if show_all or metadata['status'] != 'completed':
                        projects.append(metadata)
        
        return projects
    
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
    """Foundry OS - The AI Empire Command Center"""
    ctx.obj = FoundryOS()
    ctx.obj.ensure_directories()

@cli.command()
def version():
    """Show Foundry OS version"""
    click.echo(f"Foundry OS v{__version__}")
    click.echo("The AI Empire Command Center")

@cli.command()
@click.argument('name')
@click.option('--template', '-t', help='Project template to use')
@click.pass_obj
def new(foundry: FoundryOS, name: str, template: Optional[str]):
    """Create a new project"""
    try:
        project = foundry.create_project(name, template)
        click.echo(f"✅ Created project '{name}' [{project['id']}]")
        
        if template:
            click.echo(f"📋 Applied template: {template}")
            click.echo(f"👥 Assigned agents: {', '.join(project['agents'])}")
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
        assignment = foundry.assign_agent(task, project, agent)
        click.echo(f"✅ Task assigned [{assignment['id']}]")
        click.echo(f"📋 Task: {task}")
        click.echo(f"👤 Agent: {agent}")
        click.echo(f"📁 Project: {project}")
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)

@cli.command()
@click.option('--all', is_flag=True, help='Show all projects including completed')
@click.pass_obj
def status(foundry: FoundryOS, all: bool):
    """Show project status"""
    projects = foundry.get_status(show_all=all)
    
    if not projects:
        click.echo("No projects found.")
        return
    
    click.echo("\n📊 Project Status Report")
    click.echo("=" * 60)
    
    for project in projects:
        status_emoji = {
            'initialized': '🆕',
            'in_progress': '🔄',
            'completed': '✅',
            'paused': '⏸️'
        }.get(project['status'], '❓')
        
        click.echo(f"\n{status_emoji} {project['name']} [{project['id']}]")
        click.echo(f"   Status: {project['status']}")
        click.echo(f"   Created: {project['created_at'][:10]}")
        
        if project.get('agents'):
            click.echo(f"   Agents: {', '.join(project['agents'])}")

@cli.command()
@click.pass_obj
def init(foundry: FoundryOS):
    """Initialize Foundry OS in the current system"""
    click.echo("🏗️  Initializing Foundry OS...")
    
    # Ensure all directories exist
    foundry.ensure_directories()
    
    # Create initial config if not exists
    if not CONFIG_FILE.exists():
        config = foundry.get_default_config()
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
    
    # Create a welcome file
    welcome_file = foundry.hub_dir / 'README.md'
    if not welcome_file.exists():
        welcome_content = """# Foundry OS - AI Empire Hub

Welcome to your AI Empire Command Center!

## Quick Start

1. Create a new project:
   ```
   foundry new "My Awesome Project" --template=saas_launch
   ```

2. Assign tasks to agents:
   ```
   foundry assign "Build landing page" --project=my_awesome_project --agent=app_factory_specialist
   ```

3. Check status:
   ```
   foundry status
   ```

## Directory Structure

- `/agents` - AI agent modules
- `/projects` - Active projects
- `/templates` - Project templates
- `/shared-context` - Inter-agent communication
- `/memory-bank` - Shared knowledge base
- `/metrics` - Performance metrics
- `/logs` - System logs

## Next Steps

Run `foundry create-agent` to start building your AI team!
"""
        with open(welcome_file, 'w') as f:
            f.write(welcome_content)
    
    click.echo(f"✅ Foundry OS initialized at: {foundry.hub_dir}")
    click.echo("\nRun 'foundry --help' to see available commands.")

if __name__ == '__main__':
    cli()