# Survey on Large Language Model (LLM) Agents and Their Use of External Tools

## TL;DR
- LLM agents represent autonomous systems leveraging large language models combined with external tools to perform multi-step, complex tasks with reasoning, planning, and execution capabilities [1][2][3].
- Tool use in LLM agents has evolved from simple single-tool calls to sophisticated multi-tool orchestration frameworks including modular cooperative agents and continuous tool knowledge pre-training [4][5][6][7][8].
- Evaluation methods and benchmarks focus on correctness, trajectory-aware metrics, multi-turn dialogues, and safety, addressing challenges such as scaling, failure modes, and environment variability [9][10][11][12][13].
- Architectural patterns emphasize layered scaffolds, mediation protocols for data and tool integration, and security-enhanced modular LLM frameworks [14][15][16].
- Open problems include robust adversarial defense, generalization across tool domains, transparent planning with human feedback, and standardized unified evaluation frameworks for reproducible benchmarking [17][9][18].

## Background
Large Language Models (LLMs) have transformed AI capabilities, and integrating them as autonomous agents capable of tool use is a fast-growing research area. LLM agents extend pure language understanding by dynamically interacting with external applications, APIs, experimental apparatus, and software tools. This enhances their effectiveness for real-world applications requiring multi-step task management, domain-specific knowledge, and real-time data access.

## 1. Landscape of LLM Agents
Research categorizes LLM agents based on architecture, intrinsics, and interaction modes. Architectures range from simple prompt chains to multi-agent collaborative frameworks comprising specialized planner, executor, and reviewer roles [19][20]. Some models deploy dual-LLM design patterns to enhance security by isolating planning and execution responsibilities [14].

Agents are classified into categories such as personal assistants managing memory and tools with continuous learning [21], asynchronous models handling parallel tasks and streaming inputs [22], and domain-specific agents targeting complex scientific or robotic control domains [23][24].

Capabilities include long-horizon planning with tools, reasoning, adaptation to dynamic environments, and execution assurance via device contracts and mediation layers [1][15][16]. There are efforts to deploy such agents in production scientific facilities and open-source robotics [23][24].

## 2. Tool Use Approaches and Techniques
Tool use paradigms have progressed from prompting-based plug-and-play to supervised tool learning and reinforcement-driven policy learning schemes [18]. Integration methods leverage embedded tool descriptions, API-based invocation, and retrieval-enhanced dynamic selection frameworks to scale multi-tool agents [4].

Advanced frameworks like CONAGENTS utilize cooperative multi-agent protocols with grounding, execution, and review agents communicating adaptively for error correction and flexibility [19][5]. Tool learning benefits from continuous pre-training on massive tool knowledge corpora, improving generalization beyond pattern matching [7]. Automated tool encapsulation pipelines transform documentation into reliable function calls executable by LLMs [6].

Key design practices recommend clear tool boundaries, namespace conventions, context-specific outputs, and iterative prompt-tool refinement cycles to maximize performance and robustness [25].

## 3. Evaluation, Benchmarks, and Challenges
Benchmarks have evolved to encompass trajectory-aware metrics reflecting the correctness of multi-step tool invocation sequences with length, parameter correctness, and execution order evaluation [12]. Tool invocation is assessed via metrics such as Invocation Accuracy, Tool Selection Accuracy, and Parameter F1 scores [9][10][11].

Datasets and benchmarks cover general-purpose multi-tool planning (e.g., AAAR-1.0, TaskBench), domain-specific challenges, and interactive stateful evaluation suites simulating real-world conversational agents [10][13].

Challenges include scaling to long tool sequences, mitigating cascading errors, handling imperfect instructions, and establishing reproducible evaluation substrates isolating LLM capabilities from scaffold and environment confounders [9][12][18]. Unified infrastructures like AgentCompass aim to standardize benchmarking and provide transparent failure diagnostics [9].

## 4. Architectural Patterns and Security
Security concerns in tool-using LLM agents are addressed through dual-LLM quarantining frameworks and resource authorization via digital twins to prevent malicious tool exploitation and enforce sandboxing [14][26][17]. Execution assurance relies on device capability contracts ensuring robust operation under uncertain and dynamic conditions [15].

Architectural mediation mechanisms align LLM agent workflows with data spaces respecting governance and interoperability protocols [16]. Frontend-backend designs facilitate low-latency interaction for conversational speech-enabled tool use [27].

## 5. Trends and Open Problems
- Robust defenses against adversarial prompt and memory attacks remain critical, with emerging universal defense patterns but requiring further exploration [17].
- Generalization to diverse tool domains with minimal engineering and better pre-training integration is needed to expand applicability [7].
- Transparent planning combined with human feedback and multi-agent coordination is promising for improving reliability and interpretability [19][5].
- Standardized unified evaluation frameworks to isolate LLM ability from scaffolding effects are necessary for reproducible research and fair comparisons [9][18].
- Extending multi-agent collaboration and tool-use to embodied and asynchronous agents with streaming and real-time constraints is an open challenge [22][20].

---

This survey consolidates recent advances across three major source families (arxiv, hf-search, web) providing a rigorous multi-perspective understanding of LLM agents and their interaction with external tools for complex tasks.

---

## References
[1] Evaluating Local Language Model Agents for Reproducible Data Engineering. arxiv. https://arxiv.org/abs/2610.11482 (2026-10-08)
[2] Securing Computer-Use Agents Against Branch Steering Attacks. arxiv. https://arxiv.org/abs/2610.03089 (2026-10-02)
[3] Pincer: Resource Authorization for Agents using a Digital Twin. arxiv. https://arxiv.org/abs/2610.02569 (2026-10-01)
[4] Harness Evolution as Learning: Approximation, Generalization, and Optimization Limits of Self-Improving Personal Agents. arxiv. https://arxiv.org/abs/2609.36892 (2026-09-29)
[5] Strategies for Deploying AI Agents in Production at Scientific User Facilities. arxiv. https://arxiv.org/abs/2609.36362 (2026-09-28)
[6] LLMs are General Asynchronous Agents. arxiv. https://arxiv.org/abs/2609.35427 (2026-09-28)
[7] ADF-EA: A Unified Execution Assurance System for Agent Device Foundation. arxiv. https://arxiv.org/abs/2609.30691 (2026-09-25)
[8] Survey: Paradigms of Tool Use for LLM Agents. arxiv. https://arxiv.org/abs/arxiv-2604.00835 (n.d.)
[9] Bridging LLM Agents and Data Spaces: An Architectural Mediation Approach using the Model Context Protocol. arxiv. https://arxiv.org/abs/2609.30341 (2026-09-24)
[10] A frontend-backend architecture for tool calls in full-duplex speech models. arxiv. https://arxiv.org/abs/2609.19334 (2026-09-16)
[11] Bridging Thought and Action: Taming Long-Horizon Instability in Open-Source LLM Agents with a MetaTool-Enhanced ROS Framework. arxiv. https://arxiv.org/abs/2609.13335 (2026-09-11)
[12] Reward Hacking Benchmark: Measuring Exploits in LLM Agents with Tool Use. hf-search. https://huggingface.co/papers/2605.02964 (2026-05-03)
[13] A Review of Prominent Paradigms for LLM-Based Agents: Tool Use (Including RAG), Planning, and Feedback Learning. arxiv. https://arxiv.org/abs/2406.05804 (n.d.)
[14] The Evolution of Tool Use in LLM Agents: From Single-Tool Call to Multi-Tool Orchestration. arxiv. https://arxiv.org/abs/2603.22862 (n.d.)
[15] Learning to Use Tools via Cooperative and Interactive Agents with Large Language Models (CONAGENTS). arxiv. https://arxiv.org/abs/findings-emnlp.624 (n.d.)
[16] Multi-Agent Collaboration Mechanisms: A Survey of LLMs. arxiv. https://arxiv.org/abs/2501.06322 (2025-01-10)
[17] Building Effective AI Agents (Anthropic blog post). web. https://www.anthropic.com/engineering/building-effective-agents (2024-12-19)
[18] Evaluation and Benchmarking of LLM Agents: A Survey. hf-search. https://huggingface.co/papers/arxiv:2507.21504 (2025-07-29)
[19] ACEBench: A Comprehensive Evaluation of LLM Tool Usage. hf-search. https://huggingface.co/papers/HF_paper_2501.12851 (2025-01-22)
[20] T-Eval: Evaluating Tool Utilization Capability Step by Step. hf-search. https://huggingface.co/papers/HF_paper_2407.10499 (2024)
[21] TRAJECT-Bench: Trajectory-aware Benchmark for Tool Use in LLM Agents. arxiv. https://arxiv.org/abs/arxiv:2510.04550 (2025-10-06)
[22] ToolSandbox: Stateful Conversational Interactive Evaluation Framework. web. https://github.com/apple/ToolSandbox (N/A)
[23] Universal Defenses for Tool-Integrated LLM Agents Against Adversarial Attacks. arxiv. https://arxiv.org/abs/2609.16098 (2026-09-14)
[24] Evaluating LLM-based AI agents integrated with materials synthesis tools. arxiv. https://arxiv.org/abs/2608.29309 (2026-08-29)
[25] Tangent: An Empirical Study of Testing Practices for LLM-Based Agent Applications. arxiv. https://arxiv.org/abs/2608.08413 (2026-08-09)
[26] Writing effective tools for AI agents—using Claude as an example. web. https://www.anthropic.com/engineering/writing-tools-for-agents (2025-09-11)
[27] Learning to Use Tools via Cooperative and Interactive Agents with Large Language Models. web. https://aclanthology.org/2024.findings-emnlp.624.pdf (n.d.)
