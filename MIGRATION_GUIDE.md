# Migration Guide: Transferring to GoalieScout-BDC-2026 Repository

This guide provides step-by-step instructions for transferring the GoalieScout-BDC-2026 project from the current repository to the new `GoalieScout-BDC-2026` repository.

## Overview

All the BDC 2026 work currently resides in the `copilot/adapt-project-for-bdc-2026` branch of the `UtahNetScout/GoalieScout` repository. This needs to be transferred to a new dedicated repository `UtahNetScout/GoalieScout-BDC-2026`.

## Prerequisites

1. Ensure the new repository `GoalieScout-BDC-2026` has been created on GitHub
2. You have write access to the new repository
3. Git is installed and configured on your local machine

## Method 1: Push Branch to New Repository (Recommended)

This method preserves all commit history and is the cleanest approach.

### Step 1: Clone the Current Repository

```bash
# Clone the current repository
git clone https://github.com/UtahNetScout/GoalieScout.git
cd GoalieScout

# Checkout the BDC 2026 branch
git checkout copilot/adapt-project-for-bdc-2026
```

### Step 2: Add New Repository as Remote

```bash
# Add the new repository as a remote
git remote add bdc2026 https://github.com/UtahNetScout/GoalieScout-BDC-2026.git

# Verify remotes
git remote -v
```

### Step 3: Push to New Repository

```bash
# Push the current branch to the new repository as main
git push bdc2026 copilot/adapt-project-for-bdc-2026:main

# Or if you want to keep the branch name
git push bdc2026 copilot/adapt-project-for-bdc-2026:copilot/adapt-project-for-bdc-2026
```

### Step 4: Verify the Transfer

```bash
# Clone the new repository to verify
cd ..
git clone https://github.com/UtahNetScout/GoalieScout-BDC-2026.git
cd GoalieScout-BDC-2026

# Verify all files are present
ls -la
```

## Method 2: Using the Automated Migration Script

We've provided an automated script to handle the migration:

```bash
# Run the migration script
chmod +x migrate_to_new_repo.sh
./migrate_to_new_repo.sh
```

## Method 3: Fresh Repository with Full History

If you want to start fresh with only the BDC 2026 work:

### Step 1: Create a New Local Repository

```bash
# Create a fresh clone
git clone --branch copilot/adapt-project-for-bdc-2026 https://github.com/UtahNetScout/GoalieScout.git GoalieScout-BDC-2026-temp
cd GoalieScout-BDC-2026-temp

# Remove the old remote
git remote remove origin

# Add the new repository as origin
git remote add origin https://github.com/UtahNetScout/GoalieScout-BDC-2026.git
```

### Step 2: Push to New Repository

```bash
# Push everything to the new repository
git push -u origin copilot/adapt-project-for-bdc-2026

# Or push as main branch
git branch -M main
git push -u origin main
```

## Files to Be Transferred

The following files and directories will be transferred:

### Documentation (6 files)
- ✅ `README.md` (updated with BDC 2026 section)
- ✅ `README_BDC_2026.md` (8.5KB - complete guide)
- ✅ `USAGE_EXAMPLES.md` (6.7KB - practical examples)
- ✅ `QUICKSTART.md` (2.1KB - quick start)
- ✅ `PROJECT_SUMMARY.md` (7.8KB - technical overview)
- ✅ `IMPLEMENTATION_COMPLETE.md` (8.9KB - completion summary)

### Configuration Files
- ✅ `.env.example` (environment configuration template)
- ✅ `requirements.txt` (Python dependencies)
- ✅ `.gitignore` (Git ignore rules)

### Source Code
- ✅ `player_movement_scout.py` (main analysis script)
- ✅ `test_system.py` (test suite)
- ✅ `src/ai_providers/` (AI provider implementations)
  - `__init__.py`
  - `openai_provider.py`
  - `anthropic_provider.py`
  - `ollama_provider.py`
  - `factory.py`
- ✅ `src/data/` (data loading module)
  - `__init__.py`
  - `loader.py`
- ✅ `src/metrics/` (movement metrics)
  - `__init__.py`
  - `movement.py`
- ✅ `src/reports/` (report generation)
  - `__init__.py`
  - `generator.py`
- ✅ `src/visualization/` (plotting)
  - `__init__.py`
  - `plotter.py`

### Data Directories
- ✅ `sample_data/.gitkeep` (placeholder for data files)
- ✅ `config/` (configuration directory)

### Sample Output (Optional - not in git)
- `output/` (generated reports - excluded by .gitignore)
- `sample_data/*.csv` (sample data files - excluded by .gitignore)
- `sample_data/*.parquet` (sample data files - excluded by .gitignore)

## Post-Migration Steps

### 1. Update Repository Settings

After the migration, update the new repository settings on GitHub:

1. **Repository Description**: "AI-powered hockey player movement analysis for Big Data Cup 2026"
2. **Topics**: Add tags like `hockey`, `big-data-cup`, `player-movement`, `ai`, `scouting`
3. **Website**: Add link if applicable
4. **README**: Verify it displays correctly on GitHub

### 2. Update README.md

Update the README in the new repository to reflect the new repository name:

```bash
# In the new repository
# Update any references from 'GoalieScout' to 'GoalieScout-BDC-2026'
# Update clone URLs in documentation
```

### 3. Set Up Branch Protection (Optional)

If you want to protect the main branch:
1. Go to Settings → Branches
2. Add branch protection rules for `main`
3. Enable options like "Require pull request reviews"

### 4. Configure GitHub Actions (Optional)

If you want to add CI/CD:
1. Create `.github/workflows/` directory
2. Add workflow files for testing, linting, etc.

### 5. Verify Functionality

After migration, verify everything works:

```bash
# In the new repository
cd GoalieScout-BDC-2026

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_system.py

# Run main script
python player_movement_scout.py
```

## Verification Checklist

After migration, verify:

- [ ] All 25+ files are present in the new repository
- [ ] README.md displays correctly on GitHub
- [ ] `requirements.txt` is accessible
- [ ] Source code structure is intact (`src/` with 5 subdirectories)
- [ ] Documentation files are all present
- [ ] `.gitignore` is working correctly
- [ ] Test suite runs successfully: `python test_system.py`
- [ ] Main script runs: `python player_movement_scout.py`
- [ ] Commit history is preserved (if using Method 1 or 3)

## Updating Clone URLs

After migration, update clone commands in documentation:

**Old:**
```bash
git clone https://github.com/UtahNetScout/GoalieScout.git
```

**New:**
```bash
git clone https://github.com/UtahNetScout/GoalieScout-BDC-2026.git
```

## Common Issues and Solutions

### Issue 1: Authentication Failed

**Problem:** Git push fails with authentication error

**Solution:**
```bash
# Use personal access token
git remote set-url origin https://YOUR_USERNAME:YOUR_TOKEN@github.com/UtahNetScout/GoalieScout-BDC-2026.git

# Or use SSH
git remote set-url origin git@github.com:UtahNetScout/GoalieScout-BDC-2026.git
```

### Issue 2: Branch Already Exists

**Problem:** Branch already exists in new repository

**Solution:**
```bash
# Force push (use with caution)
git push -f bdc2026 copilot/adapt-project-for-bdc-2026:main

# Or delete remote branch first
git push bdc2026 :main
git push bdc2026 copilot/adapt-project-for-bdc-2026:main
```

### Issue 3: Large Files

**Problem:** Push fails due to large files

**Solution:**
```bash
# Check for large files
find . -type f -size +50M

# Remove them from git history if needed
git filter-branch --tree-filter 'rm -f path/to/large/file' HEAD
```

## Maintaining Both Repositories

If you want to keep the original GoalieScout repository:

1. **Original Repository**: Focus on goalie-only scouting
2. **New Repository**: Focus on BDC 2026 player movement analysis

You can reference the new repository in the original:

```markdown
## Related Projects

- [GoalieScout-BDC-2026](https://github.com/UtahNetScout/GoalieScout-BDC-2026) - 
  Big Data Cup 2026 adaptation with multi-position player movement analysis
```

## Support

If you encounter issues during migration:

1. Check GitHub's [repository transfer documentation](https://docs.github.com/en/repositories)
2. Review Git's [remote documentation](https://git-scm.com/docs/git-remote)
3. Open an issue in the new repository for help

## Summary

The migration process should take approximately **5-10 minutes** using Method 1 (recommended). The automated script (Method 2) can reduce this to **2-3 minutes**. After migration, verify all files and functionality before announcing the new repository.

---

**Last Updated:** 2026-01-30
**Migration Status:** Ready for execution
