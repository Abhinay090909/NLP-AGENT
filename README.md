# CSE 476 Final Project — General Purpose Reasoning Agent

A reasoning agent that solves questions across five domains using nine inference-time techniques.

## Setup

1. Clone the repo
git clone https://github.com/Abhinay090909/NLP-AGENT.git
cd NLP-AGENT

2. Install dependencies
pip install -r requirements.txt

3. Create a .env file in the root directory
cp .env.example .env

Then open .env and add your ASU SOL API key:
OPENAI_API_KEY=your_key_here
API_BASE=https://openai.rc.asu.edu/v1
MODEL_NAME=qwen3-30b-a3b-instruct-2507

Note: You must be on ASU network or connected via Cisco VPN to use the API.

## Running the Agent

To run on the full test data:
python3 solver.py

To run on a specific range of questions (for parallel runs):
python3 solver.py 0 2000
python3 solver.py 2000 4000
python3 solver.py 4000 6208

The solver saves a checkpoint every 10 questions so it can resume if interrupted.
Output is saved to cse_476_final_project_answers.json

To test on a single question:
python3 -c "
from agent.agent import solve
print(solve('What is 2 + 2?'))
"

## Project Structure

NLP-AGENT/
agent/
    __init__.py
    config.py         # API settings and global config
    utils.py          # LLM caller, call tracker, answer extraction
    techniques.py     # All 9 inference-time techniques
    agent.py          # Main solve() function with domain routing
solver.py             # Batch runner for test data
merge.py              # Merges parallel answer files
report.md             # One page project report
requirements.txt      # Dependencies

## The 9 Techniques

All techniques are in agent/techniques.py

1. Domain Routing       - detect_domain()        - classifies each question into a domain
2. Chain of Thought     - chain_of_thought()     - step by step reasoning
3. Self Consistency     - self_consistency()     - multiple answers with majority vote
4. Self Refine          - self_refine()          - generate then critique and improve
5. ReACT                - react()                - reason and use calculator tool
6. Tree of Thought      - tree_of_thought()      - generate and evaluate multiple approaches
7. Decomposition        - decomposition()        - break into sub-problems
8. Least to Most        - least_to_most()        - solve simpler problems first
9. Answer Verification  - answer_verification()  - verify and correct the answer

## Domain Strategy

| Domain            | Technique Used                        |
|-------------------|---------------------------------------|
| math              | Self Consistency + Answer Verification|
| common_sense      | Self Refine                           |
| coding            | Decomposition                         |
| future_prediction | Chain of Thought                      |
| planning          | Least to Most                         |
| other             | Tree of Thought                       |

## Requirements

- Python 3.6+
- ASU SOL API key from Voyager portal
- ASU VPN or on-campus network