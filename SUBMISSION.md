# Email Triage Environment - Round 1 Submission

## Project Overview
An OpenEnv environment for email triage tasks with 3 difficulty levels.

## Features
- **3 Tasks**: Easy (urgency), Medium (action), Hard (full triage)
- **Programmatic Graders**: Each task has a deterministic scorer (0.0-1.0)
- **Partial Rewards**: Task 2 gives 30% for urgency, 70% for action; Task 3 gives weighted scores
- **Live API**: Deployed on Hugging Face Spaces

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

## Testing Results
- **Task 1**: 1.0/1.0 (urgent classification)
- **Task 2**: 1.0/1.0 (correct action)
- **Task 3**: 1.0/1.0 (response with keywords)
- **Total Score**: 3.00/3.00

## How to Test
1. Go to `/docs`
2. Click `POST /reset` → Execute
3. Click `POST /step` → Send guess → Execute
4. Repeat for all 3 tasks
5. Check final score with `GET /state`

## Files Structure