CSE 476 Final Project Report: General Purpose Reasoning Agent
System Overview:
We built a general-purpose reasoning agent that solves arbitrary problem-solving tasks across five domains, math, common sense, coding, future prediction, and planning. The agent takes a question as input, detects its domain using an LLM call, selects the most appropriate inference-time technique for that domain, and returns a final answer

Architecture:
agent/config.py: API credentials, model name, and global settings max LLM calls, sleep between	calls
agent/utils.py: Core LLM calling functions call_llm and call_llm_turns, call counter, and answer extraction helpers extract_final_answer and clean_answer
agent/techniques.py: All 9 inference-time techniques as standalone functions
agent/agent.py: Main solve() function that routes questions right technique based on detected domain
solver.py: Batch runner that loads test data, calls the agent for each question, and saves answers

Efficiency: Average across all domains: ~2.5 calls per question
Techniques Used: 
We implemented 9 inference-time techniques, all located in agent/techniques.py:
Detect_domain (Domain Routing): Uses one LLM call to classify each question into one of five domains. This routes every question to the most suitable technique automatically.
chain_of_thought: Prompts the model to think step by step before returning the final answer. Used for future prediction questions.
self_consistency: Generates multiple independent answers using different prompts and returns the majority vote. Used for math questions to improve reliability.
self_refine: Generates an initial answer then passes it back to the model with a critique prompt to check and improve it. Used for common sense questions.
react: Interleaves reasoning steps with tool calls in a multi-turn conversation. The agent can call a calculator tool when needed and decides when to use it automatically.
tree_of_thought: Generates three different solution approaches, evaluates them, and picks the most promising one to solve fully. Used as a fallback for unclassified questions.
decomposition: Breaks the problem into smaller sub-problems, solves each, then combines them. Used for coding questions.
least_to_most: Identifies simpler prerequisite problems, solves them in order, then uses those results to solve the main problem. Used for planning questions.
answer_verification: After getting an answer, passes it back to the model to verify. If wrong, the model resolves and returns a corrected answer. Used for math questions after self consistency.

Team Contributions
Abhinay Gorla: Set up the GitHub repository and project structure, coordinated work between teammates, implemented the first three techniques (domain routing, chain of thought, self consistency), built the core utils.py with the LLM caller and call tracker, handled answer extraction logic, and ran testing and evaluation on the first 2000 questions. Also handled final merging of answer files.
Anish Goli: Implemented the next three techniques (self refine, ReACT with calculator tool support, tree of thought), worked on keeping LLM call count efficient across all domains, added the multi-turn call_llm_turns function to utils, and ran testing and evaluation on the last 2200 questions (4000-6208).
Lahari Popuri:  Implemented the final three techniques (decomposition, least to most, answer verification), worked on the domain-specific prompting strategy for each of the five domains, contributed to the agent routing logic in agent.py, and ran testing and evaluation on questions 2000-4000.

