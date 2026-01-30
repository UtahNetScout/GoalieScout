# Quick Migration Reference

## 🚀 Fast Track: 3-Minute Migration

### Option 1: Using the Automated Script (Easiest)

```bash
# From the GoalieScout repository root
./migrate_to_new_repo.sh
```

Follow the prompts and you're done! ✅

---

### Option 2: Manual Migration (5 Commands)

```bash
# 1. Checkout the BDC 2026 branch
git checkout copilot/adapt-project-for-bdc-2026

# 2. Add new repository as remote
git remote add bdc2026 https://github.com/UtahNetScout/GoalieScout-BDC-2026.git

# 3. Push to new repository (as main branch)
git push bdc2026 copilot/adapt-project-for-bdc-2026:main

# 4. Verify
git ls-remote bdc2026

# 5. Done! 🎉
```

---

## 📋 Quick Verification (After Migration)

```bash
# Clone the new repository
git clone https://github.com/UtahNetScout/GoalieScout-BDC-2026.git
cd GoalieScout-BDC-2026

# Verify setup
pip install -r requirements.txt
python test_system.py

# Should see: ✓ All Tests Passed!
```

---

## 📦 What Gets Transferred?

- ✅ 26 files (7 docs, 13 source files, 3 config, 2 scripts)
- ✅ ~2,000 lines of Python code
- ✅ Complete commit history (with Method 2)
- ✅ All documentation and examples

---

## 🔗 New Repository URL

**New location:** `https://github.com/UtahNetScout/GoalieScout-BDC-2026.git`

---

## 📚 Need More Details?

- **Full Guide:** See `MIGRATION_GUIDE.md`
- **File List:** See `FILE_MANIFEST.md`
- **Help:** Check GitHub docs or open an issue

---

## ⚡ One-Liner Clone After Migration

```bash
git clone https://github.com/UtahNetScout/GoalieScout-BDC-2026.git && cd GoalieScout-BDC-2026 && pip install -r requirements.txt && python test_system.py
```

---

**Last Updated:** 2026-01-30
