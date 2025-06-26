---
name: 🐛 Bug Report
about: Create a report to help us improve
title: '[BUG] '
labels: ['bug', 'needs-triage']
assignees: ''
---

## 🐛 Bug Description
A clear and concise description of what the bug is.

## 🔄 Steps to Reproduce
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## ✅ Expected Behavior
A clear and concise description of what you expected to happen.

## ❌ Actual Behavior
A clear and concise description of what actually happened.

## 📱 Environment
**API Version:** [e.g. 1.0.0]
**Docker Version:** [e.g. 20.10.8]
**OS:** [e.g. Ubuntu 20.04, Windows 10, macOS 12.0]
**Browser:** [if applicable - e.g. Chrome 95.0]

## 📋 API Request Details (if applicable)
```bash
# Include the exact API request that caused the issue
curl -X POST "http://localhost:8000/practice/start" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "soft_skill_id": 1, "scenario_id": 1}'
```

**Response:**
```json
{
  "error": "Error message here"
}
```

## 📊 Logs
If applicable, add logs to help explain your problem.

```
[timestamp] ERROR: Error message here
[timestamp] DEBUG: Additional context
```

## 📸 Screenshots
If applicable, add screenshots to help explain your problem.

## 💡 Possible Solution
If you have ideas on how to fix the issue, please describe them here.

## 📝 Additional Context
Add any other context about the problem here.

## ✅ Checklist
- [ ] I have searched for existing issues
- [ ] I have provided all the required information
- [ ] I have tested this with the latest version
- [ ] I have included logs/screenshots where applicable
