# GoalieScout
Hockey Goalie Scouting and Ranking System 

## Features

- Track past and current goalie scouting projects
- Manage project details including name, description, and status
- View all projects or specific project details

## Managing Your Projects

GoalieScout includes a simple project management tool to help you track your past scouting projects.

### List All Projects

To see all your past projects:

```bash
python project_manager.py list
```

### Add a New Project

To create a new scouting project:

```bash
python project_manager.py add "Project Name" "Project description goes here"
```

Example:
```bash
python project_manager.py add "2025 Junior League" "Scouting goalies for the 2025 junior league season"
```

### View Project Details

To view details of a specific project by ID:

```bash
python project_manager.py view <project_id>
```

Example:
```bash
python project_manager.py view 1
```

## Project Data

All project data is stored in `projects.json`. You can directly edit this file if needed, but it's recommended to use the project manager tool for consistency.
