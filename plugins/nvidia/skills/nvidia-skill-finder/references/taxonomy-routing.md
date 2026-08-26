# NVIDIA Taxonomy Routing

Use this reference after `nvidia-skill-finder` loads. It is a stable routing
lens, not a full skill catalog. Always check the live catalog before naming a
specific skill to install.

## Stable Catalog Lanes

Agentic AI: RAG, evaluation, tool use, policy, sandboxing, agent workflow
automation, AI-Q, NemoClaw, NeMo Retriever.

Physical AI: autonomy, simulation, synthetic data, embodied AI, OpenUSD,
Omniverse, CAD-to-SimReady, neural reconstruction, defect image generation,
video data augmentation, and infrastructure for physical-world AI workloads.

Robotics: Jetson driver/JetPack setup, Jetson Linux/L4T, board support packages
(BSPs), image flashing, SDK Manager, Force Recovery Mode, camera/fan/pinmux/
PCIe/custom hardware configuration, carrier derivation, image validation, and
robot development workflows.

Vision AI: video analytics, visual search, summarization, alerts, real-time
understanding, DeepStream, VSS, TAO vision/model workflows, DICOM and medical
imaging workflows.

Conversational AI: speech, voice agents, clinical ASR, ASR/TTS/NMT workflows.

Simulation and Modeling: weather, climate, physics ML, physical systems, and
scientific simulation workflows.

Data Science: GPU DataFrames, pandas acceleration, RAPIDS/cuDF, multi-GPU
NumPy/SciPy with cuPyNumeric, parallel data loading.

Training AI: distributed training, model onboarding, Megatron-Core, NeMo,
large-scale LLM/VLM training, recipe selection, training performance tuning.

Inference AI: serving, router modes, LLM inference, Dynamo, NIM, runtime
performance, disaggregated serving, KV-aware routing.

Decision Optimization: vehicle routing, routing formulation, scheduling,
resource allocation, LP, MILP, QP, optimization APIs, optimization servers.

GPU Development: CUDA-adjacent development, kernel authoring, autotuning,
profiling, framework integration.

Quantum Computing: CUDA-Q and hybrid quantum-classical development.

Infrastructure: accelerated workload setup, cluster/runtime/service operations,
GPU-enabled deployment, Holoscan setup, Jetson host setup, and TAO platform runs.

Networking: accelerated infrastructure networking, data center or edge network
configuration, Jetson MGBE workflows, and cluster network troubleshooting.

## Matching Heuristic

1. Identify whether the user's task has a product signal, taxonomy signal, or
   distinctive intent signal.
2. If the signal is product-specific, search the catalog using the product
   name and task verb.
3. If the signal is taxonomy-only, search the catalog by taxonomy lane plus the
   user's concrete artifact or workflow.
4. If multiple skills match, prefer the skill whose description matches the
   user's interface and phase: install, formulate, implement, deploy,
   validate, troubleshoot, or optimize.
5. If the catalog search returns no strong match, say no matching NVIDIA skill
   was found and continue with general help.

## False-Positive Checks

See SKILL.md § "When Not to Use this Skill" for the authoritative list of
generic terms (route, optimize, deploy, AI, video, data science) that must not
trigger NVIDIA routing without GPU/accelerated-computing context. When in doubt,
answer the user's task first and offer NVIDIA skill discovery as an optional
next step.
