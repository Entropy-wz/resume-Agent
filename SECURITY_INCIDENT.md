# 🚨 SECURITY INCIDENT REPORT

## Incident Details
- **Date:** 2026-06-16
- **Severity:** CRITICAL
- **Type:** API Key Exposure in Git History

## What Happened
Alibaba Cloud Qwen API key was hardcoded in test files and committed to git repository:
- **Exposed Key:** `sk-378c453bb0a04e6ab9a500452344d5a5`
- **Files:** `test_my_resume.py`, `PUSH_TO_GITHUB.md`
- **Commits:** 3 commits (aae043c, 5677913, 7b83a6c)
- **Status:** PUSHED TO GITHUB (publicly accessible)

## Immediate Actions Required

### 1. 🔴 ROTATE API KEY IMMEDIATELY
The exposed key **MUST** be revoked and replaced:

**Steps:**
1. Go to Alibaba Cloud DashScope console
2. Revoke key: `sk-378c453bb0a04e6ab9a500452344d5a5`
3. Generate new API key
4. Update local `.env` file with new key
5. **NEVER** commit the new key to git

**New .env setup:**
```bash
# In .env file (already in .gitignore)
OPENAI_API_KEY=your-new-key-here
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=qwen-plus
```

### 2. 🔴 CLEAN GIT HISTORY
The API key exists in git history and must be removed:

**Option A: Rewrite history (if not shared with others)**
```bash
cd D:/exp_all/resume-Agent

# Use git-filter-repo (recommended)
pip install git-filter-repo
git filter-repo --replace-text <(echo "sk-378c453bb0a04e6ab9a500452344d5a5==[REDACTED]==")

# Force push to GitHub
git push origin main --force
```

**Option B: Delete and recreate repository (simplest)**
```bash
# 1. Delete the GitHub repository
# 2. Remove .git directory locally
rm -rf .git

# 3. Reinitialize
git init
git add .
git commit -m "Initial commit (API key removed)"

# 4. Create new GitHub repository
git remote add origin https://github.com/Entropy-wz/resume-Agent.git
git push -u origin main
```

### 3. ✅ PREVENTIVE MEASURES TAKEN
- ✅ Removed hardcoded API key from `test_my_resume.py`
- ✅ Removed API key from `PUSH_TO_GITHUB.md`
- ✅ Updated code to read from environment variable
- ✅ Added test files to `.gitignore`
- ✅ Created this security incident report

## Files Fixed

### test_my_resume.py
**Before:**
```python
agent = ResumeScreeningAgent(
    openai_api_key="sk-378c453bb0a04e6ab9a500452344d5a5",  # ❌ EXPOSED
    threshold=70.0
)
```

**After:**
```python
import os
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("ERROR: OPENAI_API_KEY not set")
    return

agent = ResumeScreeningAgent(
    openai_api_key=api_key,  # ✅ SAFE
    threshold=70.0
)
```

### .gitignore additions
```
test_my_resume.py
test_debug.py
create_test_resume.py
```

## Risk Assessment

### Current Risk: 🔴 HIGH
- API key is **publicly accessible** on GitHub
- Anyone can use it to make API calls
- Potential for unauthorized usage and costs

### After Mitigation: 🟢 LOW
- Once key is rotated: exposed key becomes useless
- After history rewrite: no traces in git
- Future commits: protected by .gitignore

## Lessons Learned

### ❌ What Went Wrong
1. Hardcoded API key in test files
2. Test files not in .gitignore initially
3. No pre-commit hook to detect secrets
4. No code review before push

### ✅ Prevention for Future

1. **Never hardcode secrets**
   - Always use environment variables
   - Always use `.env` files (in .gitignore)

2. **Use pre-commit hooks**
   ```bash
   # Install pre-commit
   pip install pre-commit
   
   # Add secret detection
   # .pre-commit-config.yaml
   repos:
     - repo: https://github.com/Yelp/detect-secrets
       rev: v1.4.0
       hooks:
         - id: detect-secrets
   ```

3. **Add to .gitignore**
   - All test files with credentials
   - All .env files
   - All config files with secrets

4. **Code review checklist**
   - [ ] No hardcoded secrets
   - [ ] All secrets from environment
   - [ ] Sensitive files in .gitignore

## Timeline

| Time | Action |
|------|--------|
| 2026-06-16 09:46 | API key committed (commit aae043c) |
| 2026-06-16 10:16 | API key pushed to GitHub |
| 2026-06-16 10:50 | **INCIDENT DETECTED** |
| 2026-06-16 10:51 | Hardcoded keys removed from code |
| 2026-06-16 10:52 | Test files added to .gitignore |
| **PENDING** | **ROTATE API KEY** ⚠️ |
| **PENDING** | **CLEAN GIT HISTORY** ⚠️ |

---

## Action Items

- [ ] **URGENT:** Rotate API key in Alibaba Cloud console
- [ ] Clean git history (use git-filter-repo or recreate repo)
- [ ] Force push cleaned history
- [ ] Verify old key no longer works
- [ ] Install pre-commit hooks for secret detection
- [ ] Update team security practices

---

**Status:** 🔴 INCIDENT ACTIVE - Waiting for key rotation

**Priority:** P0 - CRITICAL
