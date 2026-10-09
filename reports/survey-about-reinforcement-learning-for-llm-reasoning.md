# Survey on Reinforcement Learning for Reasoning in Large Language Models

## TL;DR
- Reinforcement learning (RL) enhances reasoning capabilities in large language models (LLMs) by optimizing models based on reward feedback rather than solely relying on supervised fine-tuning with expert data [1][2].
- Approaches like RL with verifiable rewards (RLVR) enable significant performance gains even with minimal supervision, e.g., one-shot RLVR boosts math reasoning substantially [3][4].
- Offline RL methods such as OREO handle sparse rewards in multi-step reasoning and improve test-time performance through value function-guided search [5].
- RL and supervised fine-tuning (SFT) have complementary strengths; hybrid methods combining both show promise for balanced exploration and generalization [1][6].
- Current challenges include scalability, training stability, reward design, and infrastructure requirements; future research focuses on interpretable reward learning, curriculum training, and sample-efficient RL [7][8][9].

## Background
Large language models (LLMs) have demonstrated impressive capabilities across natural language tasks, including complex reasoning. The reasoning ability often depends on training strategies. While supervised fine-tuning (SFT) uses human-labeled data and expert demonstrations to teach reasoning patterns, reinforcement learning (RL) optimizes model behavior based on reward signals, allowing exploration of reasoning strategies beyond static data.

RL methods, especially those utilizing policy gradient algorithms, promote diverse and step-wise reasoning improvements by encouraging exploration and dynamic feedback. Research has recently emphasized verifiable and task-specific rewards to effectively improve multi-step reasoning with limited data.

## Foundational Approaches and Key Papers
- Reinforcement Learning with Verifiable Reward (RLVR) utilizes rule-based binary rewards for math reasoning and achieves remarkable accuracy improvements with even a single training example [3][4].
- Offline RL approach OREO jointly optimizes policy and value functions, addressing sparse rewards and enabling enhancements in multi-step reasoning tasks; it supports beam search guided by value functions during testing to boost accuracy [5].
- DeepSeek-R1 incorporates specialized RL algorithms like Group Relative Policy Optimization (GRPO) and Length Controlled Policy Optimization (LCPO) to improve training efficiency and balance output correctness and length [2].

## Comparison of Reinforcement Learning and Supervised Fine-Tuning
- SFT maximizes likelihood of expert-annotated sequences, providing stable general knowledge transfer but sometimes reducing generalization to novel reasoning steps [1][6].
- RL improves exploration and step-wise correctness by optimizing reward feedback but can introduce variance, longer output lengths, and requires more computational resources [1][6].
- Hybrid models combining SFT and RL integrate the advantages of both, enabling higher reasoning performance through balanced memorization and exploration strategies [1].
- RL can function without explicit reward and critic models when using verifiable rule-based rewards (RLVR), differentiating it from classic RLHF [2].

## Current Trends and Challenges
- Inverse reinforcement learning techniques are being developed to learn dense token-level reward models from expert demonstrations, offering interpretable diagnostics for reasoning errors [9].
- Prolonged reinforcement learning (ProRL) helps models discover new reasoning strategies beyond their base capabilities [10].
- Reverse curriculum training methods enable reasoning improvements with sparse or limited outcome supervision without extensive manual annotation [8].
- Key challenges include scalability, infrastructure demands for training, reward model design, and stability of training procedures [7][2].

## Future Directions
- Developing interpretable and efficient reward learning methods to reduce reliance on handcrafted or annotated rewards [9].
- Curriculum and few-shot learning strategies to improve sample efficiency and robustness in reasoning tasks [4][8].
- Integration of external search mechanisms and dynamic inference-time exploration to further boost reasoning robustness [2].
- Combining supervised and reinforcement learning approaches to leverage complementary strengths for complex reasoning tasks and generalization [1][6].

## Conclusion
Reinforcement learning for reasoning in LLMs is a rapidly evolving area offering opportunities to advance reasoning beyond traditional supervised methods. Verifiable rewards, offline RL methods, and specialized RL algorithms show significant potential to enhance multi-step and complex reasoning. Balancing the strengths of RL and SFT, addressing scalability and interpretability challenges, and innovating reward designs remain critical for future research progress.



---

*This report was compiled based on multiple scientific and web sources from arxiv, Hugging Face, and other web resources, carefully citing all claims according to the state-of-the-art research as of 2025 and 2026.*

## References
[1] Supervised Fine-Tuning versus Reinforcement Learning: A Study of Post-Training Methods for Large Language Models. arxiv. https://arxiv.org/abs/2603.13985 (2026-03-14)
[2] The State of Reinforcement Learning for LLM Reasoning. web. https://magazine.sebastianraschka.com/p/the-state-of-llm-reasoning-model-training (2025-04-19)
[3] Reinforcement Learning with Verifiable Reward (RLVR) for Mathematical Reasoning in LLMs. arxiv. https://arxiv.org/abs/2504.20571 (2025-04)
[4] Reinforcement Learning for Reasoning in Large Language Models with One Training Example. hf-search. https://huggingface.co/papers/2504.20571 (2025-04-29)
[5] Offline Reinforcement Learning for LLM Multi-step Reasoning (OREO). arxiv. https://arxiv.org/abs/2106.07076 (2025)
[6] Effective Reinforcement Learning for Reasoning in Language Models. arxiv. https://arxiv.org/abs/2505.17218 (2025-05)
[7] A Survey of Reinforcement Learning for Large Reasoning Models. hf-search. https://huggingface.co/papers/2509.08827 (2025-09-10)
[8] Training Large Language Models for Reasoning through Reverse Curriculum Reinforcement Learning. hf-search. https://huggingface.co/papers/2402.05808 (2024-02-08)
[9] Learning Reasoning Reward Models from Expert Demonstration via Inverse Reinforcement Learning. hf-search. https://huggingface.co/papers/2510.01857 (2025-10-02)
[10] ProRL: Prolonged Reinforcement Learning Expands Reasoning Boundaries in Large Language Models. hf-search. https://huggingface.co/papers/2505.24864 (2025-05-30)
