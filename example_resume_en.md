---
name: Shiqi Li
phone: +86 158 6966 5100
email: mayeggx@mail.ustc.edu.cn
age: 24
gender: Male
country: China
language: en
layout: compact
---

# Education
## University of Science and Technology of China [985] | M.Eng. in Software Engineering | Sep 2024 - Jun 2027 | Suzhou, China

## Jiangnan University [211] | B.Eng. in Textile Engineering | Sep 2020 - Jun 2024 | Wuxi, China

# Language Proficiency
- **English:** Proficient in reading and writing; fluent in listening and speaking. CET-6: 520.
- **Japanese:** Proficient in reading and writing; fluent in listening and speaking. JLPT N1: 136.

# Internship Experience

## Tencent Technology (Shenzhen) Co., Ltd. | Backend Engineering Intern, CSIG Yuanbao Core Services Team | May 2026 - Present | Shenzhen, China
### LLM Wiki: Knowledge Management and Retrieval Platform
Built an AI-native knowledge management and retrieval platform for engineering workflows from the ground up. The platform provides durable development context for AI coding by processing code repositories, iWiki documents, APM traces, incident-response SOPs, product requirements, and technical design documents.
- **Multi-source knowledge pipeline and cross-repository search:** Designed and implemented the end-to-end knowledge pipeline, from data ingestion and parsing to compilation and Wiki artifact generation. Following the Google OKF approach, compiled five heterogeneous knowledge sources into traceable concept cards; enabled on-demand agent access through hierarchical directories, routing, and section indexes. Integrated CodeGraph and fff for cross-repository code search, call-chain tracing, and incremental synchronization across 300+ repositories and 3,000+ iWiki documents, producing 8,000+ Wiki pages.
- **Retrieval evaluation and ranking optimization:** Built an automated evaluation set of 400 retrieval queries and led bad-case analysis and ranking improvements. Structured samples by knowledge source, task intent, task complexity, and query formulation to cover core engineering Q&A scenarios. Replaced full scans, ineffective Chinese tokenization, and raw term-frequency ranking with BM25, CJK tokenization, IDF-based high-frequency-term downweighting, proximity boosting, and a positional inverted index; improved Recall@5 from 61.8% to 81.6%, Precision@5 from 54.2% to 72.4%, and MRR@10 from 0.47 to 0.71.

## Tencent Technology (Shenzhen) Co., Ltd. | Backend Engineering Intern, CDG Payments Infrastructure Productivity Team | Aug 2025 - Apr 2026 | Shenzhen, China

### Production Incident Diagnosis Agent
Contributed to an AI-powered production incident diagnosis system for backend microservices. The system coordinates multiple agents to collect evidence from APM traces, logs, code, configuration, and historical SOPs, then identifies root causes. Focused on performance and production hardening of the log-query path to reduce tool-call overhead and external API throttling.
- **Multi-agent incident orchestration:** Refined responsibility boundaries among the primary agent and trace-analysis, log-analysis, code-analysis, and metrics sub-agents. Defined three execution paths: parallel trace and log analysis, trace-guided log analysis, and direct log lookup. Connected APM spans, service logs, code and configuration, and historical SOPs through parameterized context passing, sidecar-service identification, and cross-evidence validation, with the primary agent making the final root-cause determination.
- **Production-grade log retrieval:** Consolidated environment discovery, service discovery, and log retrieval from model-driven, multi-round MCP calls into a single script-based Skill. Added environment and time-window detection from trace IDs, time slicing, concurrent fallback, and three-tier queries for ERROR logs, keywords, and full logs. Implemented adaptive rate limiting by query span, cross-process shared throttling, and exponential backoff for constrained APIs; reduced trace-location time from 30s to 18s and average end-to-end diagnosis time from 804s to 682s.

### AI Workflow Delivery Assistant
Designed an AI-native workflow execution engine based on spec-driven development to let AI agents drive the full engineering delivery lifecycle. Built for platform teams with diverse development scenarios, the system improves consistency, traceability, and delivery quality in AI-assisted development. Responsible for the workflow engine and automated evaluation platform.
- **Workflow engine and customizable workflows:** Exposed workflow capabilities as standard tools through MCP. Built a Pipeline -> Stage -> Step three-level state machine driven by MCP tools, separating state management from business logic. Added quality gates and Skill entry/exit validation for layered artifact quality assurance; teams can compose their own delivery processes with workflow configuration and Skills, while agents execute each step and enforce quality requirements.
- **Automated evaluation platform:** Designed a distributed microservice architecture with management and compute nodes to run end-to-end, unattended execution and quality evaluation across development stages. Used scripts to simulate complete workflows on development machines and compute-node hooks to calculate and report process metrics when each step completes.

# Technical Skills
- **Programming:** Proficient in Go, including common data structures, garbage collection, and GMP scheduling; working knowledge of Python and large language model fundamentals.
- **Databases and caching:** Strong understanding of MySQL storage engines, indexes, transactions, locks, logging, and MVCC; familiar with Redis data structures, replication, Sentinel, Cluster, and persistence.
- **Systems and networking:** Familiar with computer networking fundamentals and HTTP/HTTPS, TCP, and DNS; experienced with Git, Docker, Linux command-line tools, and backend engineering workflows.
