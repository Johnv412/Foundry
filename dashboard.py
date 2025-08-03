#!/usr/bin/env python3
"""
🏭 Foundry OS Dashboard - AI Empire Command Center
The most advanced AI business empire management dashboard
"""

import streamlit as st
import json
import os
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import re

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

# Import our Foundry OS
try:
    from foundry_v11 import FoundryOS
except ImportError:
    # Create a simple mock FoundryOS for the dashboard
    class FoundryOS:
        def __init__(self):
            self.hub_dir = Path("ai-empire-hub")
            self.projects_dir = self.hub_dir / "projects"
        
        def ensure_directories(self):
            self.projects_dir.mkdir(parents=True, exist_ok=True)
        
        def discover_projects(self):
            """Discover all projects from JSON manifests"""
            projects = []
            if not self.projects_dir.exists():
                return projects
            
            for manifest_file in self.projects_dir.glob("*.json"):
                try:
                    with open(manifest_file, 'r') as f:
                        projects.append(json.load(f))
                except:
                    pass
            return projects

# Page configuration
st.set_page_config(
    page_title="🏭 AI Empire Hub",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: white;
        border: 1px solid #e1e5e9;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .project-card {
        background-color: white;
        border: 1px solid #e1e5e9;
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .status-active { color: #10b981; font-weight: bold; }
    .status-development { color: #f59e0b; font-weight: bold; }
    .status-production { color: #3b82f6; font-weight: bold; }
    .status-planning { color: #8b5cf6; font-weight: bold; }
    .task-high { color: #ef4444; }
    .task-medium { color: #f59e0b; }
    .task-low { color: #10b981; }
    .revenue-positive { color: #10b981; font-weight: bold; font-size: 1.2em; }
</style>
""", unsafe_allow_html=True)

class DashboardManager:
    def __init__(self):
        self.foundry = FoundryOS()
        self.foundry.ensure_directories()
        
    def parse_revenue(self, revenue_str):
        """Parse revenue string to float"""
        if not revenue_str:
            return 0.0
        if isinstance(revenue_str, (int, float)):
            return float(revenue_str)
        # Remove currency symbols and commas
        clean_str = re.sub(r'[^\d.-]', '', str(revenue_str))
        try:
            return float(clean_str) if clean_str else 0.0
        except ValueError:
            return 0.0
    
    def get_empire_analytics(self):
        """Get comprehensive empire analytics"""
        projects = self.foundry.discover_projects()
        
        # Basic metrics
        total_projects = len(projects)
        active_projects = len([p for p in projects if p.get('status') not in ['archived', 'completed']])
        
        # Revenue analysis
        total_revenue = 0
        monthly_revenue = 0
        revenue_projects = []
        
        for project in projects:
            metrics = project.get('metrics', {})
            revenue = self.parse_revenue(metrics.get('revenue', 0))
            total_revenue += revenue
            
            if revenue > 0:
                revenue_projects.append({
                    'name': project.get('projectName', 'Unknown'),
                    'revenue': revenue,
                    'status': project.get('status', 'unknown'),
                    'users': metrics.get('users', 0)
                })
        
        # Status distribution
        status_counts = {}
        for project in projects:
            status = project.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Agent workload
        agent_workload = {}
        task_distribution = {'high': 0, 'medium': 0, 'low': 0, 'critical': 0}
        
        for project in projects:
            if project.get('status') not in ['archived', 'completed']:
                # Team members
                for agent in project.get('team', []):
                    agent_workload[agent] = agent_workload.get(agent, 0) + 1
                
                # Task priorities
                for task in project.get('tasks', {}).get('active', []):
                    priority = task.get('priority', 'medium')
                    task_distribution[priority] = task_distribution.get(priority, 0) + 1
        
        # Growth metrics (simulated based on start dates)
        growth_data = []
        for project in projects:
            start_date = project.get('metrics', {}).get('startDate')
            if start_date:
                try:
                    date_obj = datetime.strptime(start_date, '%Y-%m-%d')
                    revenue = self.parse_revenue(project.get('metrics', {}).get('revenue', 0))
                    growth_data.append({
                        'date': date_obj,
                        'revenue': revenue,
                        'project': project.get('projectName', 'Unknown')
                    })
                except ValueError:
                    pass
        
        return {
            'total_projects': total_projects,
            'active_projects': active_projects,
            'total_revenue': total_revenue,
            'revenue_projects': revenue_projects,
            'status_distribution': status_counts,
            'agent_workload': agent_workload,
            'task_distribution': task_distribution,
            'growth_data': growth_data,
            'projects': projects
        }

def render_sidebar():
    """Render the sidebar with controls"""
    with st.sidebar:
        st.title("🏭 AI Empire Hub")
        st.markdown("*The Command Center*")
        
        st.divider()
        
        # Refresh controls
        st.subheader("⚡ Controls")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        with col2:
            auto_refresh = st.checkbox("Auto-refresh")
        
        if auto_refresh:
            refresh_interval = st.slider("Refresh (sec)", 30, 300, 60)
            time.sleep(refresh_interval)
            st.rerun()
        
        st.divider()
        
        # Quick stats
        dashboard = DashboardManager()
        analytics = dashboard.get_empire_analytics()
        
        st.subheader("📊 Quick Stats")
        st.metric("Total Projects", analytics['total_projects'])
        st.metric("Active Projects", analytics['active_projects'])
        st.metric("Total Revenue", f"${analytics['total_revenue']:,.0f}")
        
        st.divider()
        
        # Project creation
        st.subheader("➕ Add Project")
        
        # Simple project form
        with st.expander("Create New Project"):
            project_name = st.text_input("Project Name")
            project_type = st.selectbox("Type", [
                "SaaS_Launch_Playbook",
                "restaurant_bot", 
                "marketplace",
                "ecommerce_platform",
                "custom"
            ])
            status = st.selectbox("Status", [
                "planning", "development", "testing", 
                "production", "maintenance"
            ])
            
            if st.button("Create Project") and project_name:
                # Create manifest
                manifest = {
                    "projectName": project_name,
                    "projectType": project_type,
                    "leadStrategist": "Dashboard User",
                    "leadArchitect": "Foundry OS",
                    "status": status,
                    "description": f"Project created via dashboard on {datetime.now().strftime('%Y-%m-%d')}",
                    "metrics": {
                        "startDate": datetime.now().strftime('%Y-%m-%d')
                    },
                    "tasks": {
                        "active": [],
                        "completed": []
                    }
                }
                
                # Save manifest
                project_id = project_name.lower().replace(' ', '_').replace('-', '_')
                manifest_path = Path("ai-empire-hub/projects") / f"{project_id}.json"
                
                try:
                    with open(manifest_path, 'w') as f:
                        json.dump(manifest, f, indent=2)
                    st.success(f"✅ Created {project_name}!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        # File upload
        st.subheader("📁 Upload Manifest")
        uploaded_file = st.file_uploader("Drop JSON manifest", type=["json"])
        if uploaded_file:
            try:
                project_data = json.load(uploaded_file)
                project_name = project_data.get("projectName", "unknown")
                project_id = project_name.lower().replace(' ', '_')
                
                save_path = Path("ai-empire-hub/projects") / f"{project_id}.json"
                with open(save_path, "w") as f:
                    json.dump(project_data, f, indent=2)
                
                st.success(f"✅ Added {project_name}!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")

def render_main_dashboard():
    """Render the main dashboard content"""
    # Header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.title("🏭 AI Empire Dashboard")
        st.markdown("*Real-time business intelligence for your AI ventures*")
    
    with col2:
        st.markdown(f"**Last Updated**")
        st.markdown(f"`{datetime.now().strftime('%H:%M:%S')}`")
    
    with col3:
        st.markdown(f"**Status**")
        st.markdown("🟢 **OPERATIONAL**")
    
    # Load analytics
    dashboard = DashboardManager()
    analytics = dashboard.get_empire_analytics()
    
    if not analytics['projects']:
        st.warning("🎯 No projects found. Add your first project using the sidebar!")
        return
    
    # Empire KPIs
    st.subheader("📈 Empire Overview")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Projects", 
            analytics['total_projects'],
            delta=None
        )
    
    with col2:
        st.metric(
            "Active Projects", 
            analytics['active_projects'],
            delta=f"{analytics['active_projects'] - (analytics['total_projects'] - analytics['active_projects'])}"
        )
    
    with col3:
        st.metric(
            "Total Revenue", 
            f"${analytics['total_revenue']:,.0f}",
            delta="Growing" if analytics['total_revenue'] > 0 else None
        )
    
    with col4:
        avg_revenue = analytics['total_revenue'] / len(analytics['revenue_projects']) if analytics['revenue_projects'] else 0
        st.metric(
            "Avg Revenue", 
            f"${avg_revenue:,.0f}",
            delta=None
        )
    
    with col5:
        total_users = sum(p.get('metrics', {}).get('users', 0) for p in analytics['projects'])
        st.metric(
            "Total Users", 
            f"{total_users:,}",
            delta="Growing" if total_users > 0 else None
        )
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue by project
        if analytics['revenue_projects']:
            st.subheader("💰 Revenue by Project")
            fig = px.bar(
                pd.DataFrame(analytics['revenue_projects']),
                x='name',
                y='revenue',
                color='status',
                title="Project Revenue Distribution",
                color_discrete_map={
                    'production': '#10b981',
                    'development': '#f59e0b',
                    'planning': '#8b5cf6',
                    'active': '#3b82f6'
                }
            )
            fig.update_layout(showlegend=True, height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("💡 Add revenue metrics to your projects to see charts")
    
    with col2:
        # Status distribution
        if analytics['status_distribution']:
            st.subheader("📊 Project Status")
            fig = px.pie(
                values=list(analytics['status_distribution'].values()),
                names=list(analytics['status_distribution'].keys()),
                title="Status Distribution",
                color_discrete_map={
                    'production': '#10b981',
                    'development': '#f59e0b',
                    'planning': '#8b5cf6',
                    'active': '#3b82f6',
                    'maintenance': '#6b7280'
                }
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Agent workload
    if analytics['agent_workload']:
        st.subheader("👥 Agent Workload")
        col1, col2 = st.columns(2)
        
        with col1:
            workload_df = pd.DataFrame([
                {'Agent': agent, 'Projects': count} 
                for agent, count in analytics['agent_workload'].items()
            ])
            fig = px.bar(
                workload_df,
                x='Agent',
                y='Projects',
                title="Projects per Agent",
                color='Projects',
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Task priority distribution
            if analytics['task_distribution']:
                fig = px.pie(
                    values=list(analytics['task_distribution'].values()),
                    names=list(analytics['task_distribution'].keys()),
                    title="Task Priority Distribution",
                    color_discrete_map={
                        'critical': '#ef4444',
                        'high': '#f59e0b',
                        'medium': '#3b82f6',
                        'low': '#10b981'
                    }
                )
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
    
    # Project cards
    st.subheader("📋 Project Portfolio")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All"] + list(set(p.get('status', 'unknown') for p in analytics['projects']))
        )
    with col2:
        type_filter = st.selectbox(
            "Filter by Type",
            ["All"] + list(set(p.get('projectType', 'unknown') for p in analytics['projects']))
        )
    with col3:
        sort_by = st.selectbox("Sort by", ["Name", "Revenue", "Status", "Created"])
    
    # Filter projects
    filtered_projects = analytics['projects']
    if status_filter != "All":
        filtered_projects = [p for p in filtered_projects if p.get('status') == status_filter]
    if type_filter != "All":
        filtered_projects = [p for p in filtered_projects if p.get('projectType') == type_filter]
    
    # Sort projects
    if sort_by == "Revenue":
        filtered_projects = sorted(
            filtered_projects,
            key=lambda x: dashboard.parse_revenue(x.get('metrics', {}).get('revenue', 0)),
            reverse=True
        )
    elif sort_by == "Name":
        filtered_projects = sorted(filtered_projects, key=lambda x: x.get('projectName', ''))
    
    # Display project cards
    for project in filtered_projects:
        with st.container():
            st.markdown('<div class="project-card">', unsafe_allow_html=True)
            
            # Project header
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.subheader(f"🚀 {project.get('projectName', 'Unknown Project')}")
                st.markdown(f"**Type:** {project.get('projectType', 'Unknown')}")
                if project.get('description'):
                    st.markdown(f"*{project['description']}*")
            
            with col2:
                status = project.get('status', 'unknown')
                status_emoji = {
                    'planning': '📋', 'development': '🔨', 'testing': '🧪',
                    'production': '🚀', 'active': '⚡', 'maintenance': '🔧'
                }.get(status, '❓')
                st.markdown(f"**Status:** {status_emoji} {status.title()}")
                st.markdown(f"**Lead:** {project.get('leadStrategist', 'Unknown')}")
            
            with col3:
                metrics = project.get('metrics', {})
                revenue = dashboard.parse_revenue(metrics.get('revenue', 0))
                if revenue > 0:
                    st.markdown(f'**Revenue:** <span class="revenue-positive">${revenue:,.0f}</span>', unsafe_allow_html=True)
                
                users = metrics.get('users', 0)
                if users > 0:
                    st.markdown(f"**Users:** {users:,}")
            
            # Project details
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # URLs and links
                if project.get('liveUrl'):
                    st.markdown(f"🌐 [Live Site]({project['liveUrl']})")
                if project.get('coreRepo'):
                    st.markdown(f"📁 [Repository]({project['coreRepo']})")
                
                # Team
                team = project.get('team', [])
                if team:
                    st.markdown(f"**Team:** {', '.join(team)}")
            
            with col2:
                # Tasks
                tasks = project.get('tasks', {})
                active_tasks = tasks.get('active', [])
                completed_tasks = tasks.get('completed', [])
                
                if active_tasks:
                    st.markdown(f"**Active Tasks ({len(active_tasks)}):**")
                    for task in active_tasks[:3]:  # Show max 3 tasks
                        priority = task.get('priority', 'medium')
                        priority_emoji = {
                            'critical': '🔴', 'high': '🟠', 
                            'medium': '🟡', 'low': '🟢'
                        }.get(priority, '⚪')
                        st.markdown(f"{priority_emoji} {task.get('description', 'No description')} → {task.get('assignedTo', 'Unassigned')}")
                    
                    if len(active_tasks) > 3:
                        st.markdown(f"*... and {len(active_tasks) - 3} more tasks*")
                
                if completed_tasks:
                    st.markdown(f"✅ **Completed:** {len(completed_tasks)} tasks")
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")

def main():
    """Main dashboard application"""
    # Render sidebar
    render_sidebar()
    
    # Render main content
    render_main_dashboard()
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("🏭 **Foundry OS v1.1**")
    with col2:
        st.markdown("⚡ **PLUG-AND-PLAY System**")
    with col3:
        st.markdown(f"🕐 **{datetime.now().strftime('%Y-%m-%d %H:%M')}**")

if __name__ == "__main__":
    main()