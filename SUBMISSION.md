# Email Triage Environment - Round 1 Submission

## Project Overview
An OpenEnv environment for email triage tasks with 3 difficulty levels. AI agents learn to classify emails, choose appropriate actions, and draft responses.

## Live Demo
- **Space**: https://huggingface.co/spaces/codeBug01/email-triage-env
- **API Docs**: https://codeBug01-email-triage-env.hf.space/docs

## API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reset` | POST | Start new episode |
| `/step` | POST | Take action, get reward |
| `/state` | GET | Get current state |
| `/health` | GET | Health check |

## Tasks

### Task 1 (Easy) - Urgency Classification
- Classify email as `urgent`, `normal`, or `spam`
- Grader: Exact match → 1.0, else 0.0

### Task 2 (Medium) - Action Selection
- Choose correct action: `respond`, `archive`, `escalate`, `delete`
- Grader: 30% urgency + 70% action

### Task 3 (Hard) - Full Triage
- Classify urgency + choose action + draft response
- Grader: 20% urgency + 30% action + 50% response quality

## Testing Results
- **Task 1**: 1.0/1.0
- **Task 2**: 1.0/1.0
- **Task 3**: 1.0/1.0
- **Total Score**: 3.00/3.00

## How to Test
1. Go to `/docs`
2. Click `POST /reset` → Execute
3. Click `POST /step` → Send guess → Execute
4. Repeat for all 3 tasks
5. Check final score with `GET /state`

## Files Structure
email-triage-env/
├── app.py
├── models.py
├── server/
│ ├── init.py
│ └── environment.py
├── requirements.txt
├── Dockerfile
└── README.md


## Baseline Score
**3.00/3.00** with optimal agent

## Deployment
- **Platform**: Hugging Face Spaces
- **Container**: Docker
- **Port**: 7860