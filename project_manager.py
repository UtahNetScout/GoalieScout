#!/usr/bin/env python3
"""
GoalieScout Project Manager

A simple command-line tool to manage past and current goalie scouting projects.
"""

import json
import os
from datetime import datetime

PROJECTS_FILE = "projects.json"


def load_projects():
    """Load projects from the JSON file."""
    if not os.path.exists(PROJECTS_FILE):
        return {"projects": []}
    
    try:
        with open(PROJECTS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading projects file: {e}")
        print("Starting with empty project list.")
        return {"projects": []}


def save_projects(data):
    """Save projects to the JSON file."""
    try:
        with open(PROJECTS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        print(f"Error saving projects file: {e}")
        print("Changes were not saved.")


def list_projects():
    """Display all past projects."""
    data = load_projects()
    projects = data.get("projects", [])
    
    if not projects:
        print("No projects found. Use 'add' to create a new project.")
        return
    
    print("\n=== GoalieScout Projects ===\n")
    for project in projects:
        print(f"ID: {project['id']}")
        print(f"Name: {project['name']}")
        print(f"Description: {project['description']}")
        print(f"Created: {project['date_created']}")
        print(f"Status: {project['status']}")
        print(f"Goalies Scouted: {project.get('goalies_scouted', 0)}")
        print("-" * 50)


def add_project(name, description):
    """Add a new project."""
    data = load_projects()
    projects = data.get("projects", [])
    
    new_id = max([p['id'] for p in projects], default=0) + 1
    
    new_project = {
        "id": new_id,
        "name": name,
        "description": description,
        "date_created": datetime.now().strftime("%Y-%m-%d"),
        "status": "active",
        "goalies_scouted": 0
    }
    
    projects.append(new_project)
    data["projects"] = projects
    save_projects(data)
    
    print(f"\nProject '{name}' created successfully with ID {new_id}")


def view_project(project_id):
    """View details of a specific project."""
    data = load_projects()
    projects = data.get("projects", [])
    
    try:
        project_id_int = int(project_id)
    except ValueError:
        print(f"Error: '{project_id}' is not a valid project ID. Please provide a numeric ID.")
        return
    
    project = next((p for p in projects if p['id'] == project_id_int), None)
    
    if not project:
        print(f"Project with ID {project_id} not found.")
        return
    
    print("\n=== Project Details ===\n")
    print(f"ID: {project['id']}")
    print(f"Name: {project['name']}")
    print(f"Description: {project['description']}")
    print(f"Created: {project['date_created']}")
    print(f"Status: {project['status']}")
    print(f"Goalies Scouted: {project.get('goalies_scouted', 0)}")


def main():
    """Main entry point for the project manager."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python project_manager.py list                    - List all projects")
        print("  python project_manager.py add <name> <desc>       - Add a new project")
        print("  python project_manager.py view <id>               - View project details")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        list_projects()
    elif command == "add":
        if len(sys.argv) < 4:
            print("Error: Please provide both name and description")
            print("Usage: python project_manager.py add <name> <description>")
            return
        name = sys.argv[2]
        description = " ".join(sys.argv[3:])
        add_project(name, description)
    elif command == "view":
        if len(sys.argv) < 3:
            print("Error: Please provide project ID")
            print("Usage: python project_manager.py view <id>")
            return
        view_project(sys.argv[2])
    else:
        print(f"Unknown command: {command}")
        print("Valid commands: list, add, view")


if __name__ == "__main__":
    main()
