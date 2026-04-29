CSE 476 Final Project Report: General Purpose: Reasoning Agent

Github Link: https://github.com/Abhinay090909/NLP-AGENT

System Overview:
We built a general-purpose reasoning agent that solves problem-solving tasks across five domains: math, common sense, coding, future prediction, and planning. The agent takes a question as input, detects its domain using rule-based pattern matching, selects the most appropriate inference-time technique for that domain, and returns a final answer.

Architecture:
agent/config.py: API credentials, model name, and global settings max LLM calls, sleep between calls
agent/utils.py: Core LLM calling functions call_llm and call_llm_turns, call counter, and answer extraction helpers extract_final_answer, clean_answer, clean_code, and clean_plan
agent/techniques.py: All 9 inference-time techniques as standalone functions
agent/agent.py: Main solve() function that routes each question to the right technique based on detected domain
solver.py: Batch runner that loads test data, calls the agent for each question, and saves answers with checkpoint support
eval.py: — Evaluation script that tests accuracy per domain on dev data with configurable sample size

Techniques Used: 
We implemented 9 inference-time techniques, all located in agent/techniques.py:
Domain Routing (detect_domain): Uses one LLM call to classify each question into one of five domains. This routes every question to the most suitable technique automatically.
Chain of Thought (chain_of_thought): Prompts the model to think step by step before returning the final answer. Used for future prediction questions.
Self Consistency (self_consistency): Generates multiple independent answers using different prompts and returns the majority vote. Used for math questions to improve reliability.
Self Refine (self_refine): Generates an initial answer then passes it back to the model with a critique prompt to check and improve it. Used for common sense questions.
ReACT (react):  Interleaves reasoning steps with tool calls in a multi-turn conversation. The agent can call a calculator tool when needed and decides when to use it automatically.
Tree of Thought (tree_of_thought): Generates three different solution approaches, evaluates them, and picks the most promising one to solve fully. Used as a fallback for unclassified questions.
Decomposition (decomposition): Breaks the problem into smaller sub-problems, solves each, then combines them. Used for coding questions.
Least to Most (least_to_most): Identifies simpler prerequisite problems, solves them in order, then uses those results to solve the main problem. Used for planning questions.
Answer Verification (answer_verification): After getting an answer, passes it back to the model to verify correctness. If wrong, the model resolves and returns a corrected answer. Used for math questions after self consistency.

Domain-Specific Handlers
In addition to the 8 standard techniques, we built dedicated handlers for each domain subtype: coding_completion for function body completion with normalized indentation, 
planning_completion for multi-turn plan generation with subtype detection for logistics vs object planning, 
mcq_answer with self-consistency voting across 3 calls for multiple choice questions, 
tf_answer for true/false questions, 
context_answer for reading comprehension questions, and
future_prediction for formatting predictions as Python lists.

Efficiency
We kept LLM calls well under the 20 call limit. Calls per question by domain:
Math: 4 calls normally (self consistency ×3 + verification), up to 6 calls if fallbacks trigger (+ react + chain of thought)
Common sense MCQ: 3 calls max 
Coding: 1-2 calls
Planning: 3 calls (multi-turn)
Future prediction: 1 call
Average across all domains: ~3 calls per question, well within the 20 call budget.

Team Contributions

Abhinay Gorla: Set up the GitHub repository and project structure, coordinated work between teammates, implemented the first three techniques (domain routing, chain of thought, self consistency), built the core utils.py, handled answer extraction logic, and ran testing and evaluation on the first 2000 questions. Updated all techniques with improved prompts and token limits to increase accuracy for math and common sense.

Anish Goli: Implemented the next three techniques (self refine, ReACT with calculator tool support, tree of thought), worked on keeping LLM call count efficient across all domains, added the multi-turn call_llm_turns function to utils, and ran testing and evaluation on the last 2200 questions (4000-6208). Ran multiple tests to compare the final output answers file.

Lahari Popuri:  Implemented the final three techniques (decomposition, least to most, answer verification), worked on the domain-specific prompting strategy for each of the five domains, contributed to the agent routing logic in agent.py, and ran testing and evaluation on questions 2000-4000. Worked on improving the accuracy rate of planning and future prediction domains.

