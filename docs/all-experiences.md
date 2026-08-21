# Shaun Porwal — Complete Experience Record

Personal reference only — **not** wired into any generation script (unlike `data/resume.json`, which is the actual source for `site/resume.html`). This is the fuller, unedited work history to pull from when tailoring `data/resume.json` for a specific application, or when `data/resume.json` needs a bullet it doesn't currently have. Update by hand as things change; nothing here regenerates automatically.

Originally maintained in a separate `jobapps` repo (`resume/all_experiences.txt`); copied here so it lives alongside the resume it feeds, instead of a second repo to keep in sync.

Email: shaun.porwal@gmail.com | Phone: (732) 318-7592
Location: New York, NY | Website: shaunporwal.com
GitHub: github.com/shaunporwal | LinkedIn: linkedin.com/in/shaunporwal
Citizenship: U.S. Citizen

## Professional Experience

### Junto Technologies — Founder & Engineer
March 2026 to Present | Metuchen, NJ

- Built full-stack (design, client, server, database, authentication) chemical inventory management system (cheminventory.co); manages version-controlled regulatory compliance documents; $1M+ in yearly order lifecycle provenance
- Architected a self-hosted, autonomous multi-agent AI swarm — Tailscale-networked device fleet (NVIDIA Spark/DGX, Mac mini, Raspberry Pi) serving local LLMs via vLLM/llama.cpp — with parallel sub-agents on a shared task queue, persistent cross-session memory, a self-improving skill library, cron-scheduled autonomous runs, promptfoo-driven evals, a custom fleet-monitoring dashboard (Glances-based, plain HTML/CSS), and Apple Watch dictation for remote control over Telegram; used it to run market research, competitive analysis, and go-to-market strategy for the business
- Standardizing processes at a specialty chemicals company to achieve International Organization for Standardization (ISO) certification
- Served as translator (Mandarin/English) at CPHI Shanghai 2026 for a specialty chemicals company

### Standard Model Biomedicine — Founding Engineer
May 2025 to March 2026 | Philadelphia, PA
https://standardmodel.bio

**1. AI Agents as Application Layer for Biomedical AI Workflows**
- Built full-stack agent orchestration platform (smb-agent) with FastAPI + WebSocket backend and Next.js frontend for interactive chat, dataset/model management, training monitoring, inference, and image viewing
- Implemented agent tooling with LangGraph and OpenAI Agents Python SDK; integrated RunPod job triggering and W&B tracking for fine-tuning and inference workflows
- Added medical imaging support for DICOM/NIfTI slice rendering with segmentation/overlay views to streamline tumor-focused analysis demos and stakeholder showcases
- Created demo videos showcasing agentic capabilities for marketing
- Iterated architecture from initial Next.js app to packaged Python system with modular route managers, MCP/data-loader integrations, and production-style deployment tooling

Key challenges solved:
- Reliable LLM-agent orchestration over WebSockets for long biomedical workflows without losing state, duplicating tool calls, or failing under partial timeouts
- Safe coordination of tool execution across heterogeneous services (RunPod, W&B, Hugging Face, data loaders) with deterministic behavior and recovery from mid-run failures
- Low-latency DICOM/NIfTI slice rendering with segmentation/overlay support across inconsistent metadata and varying medical dataset structures

**2. Python Library for CT-Image-to-Survival-Prediction (smb-pipe)**
- Built smb-pipe, a reusable research library and CLI suite for MEDS-to-model pipelines including data window/object generation, multimodal preprocessing, CT embedding extraction, survival model training, and inference
- Implemented survival-specific modeling components: Cox partial likelihood loss, C-index evaluation, survival heads and MLP heads
- Added support for pre-trained Hugging Face model weights and reproducible notebook + script workflows (e.g., aortic aneurysm risk prediction)
- Packaged with docs, tests, and GPU/container workflows for researcher-facing experimentation with minimal setup

Key challenges solved:
- Determining right abstraction level: which workflow controls remain configurable vs. hard-coded defaults for reliable use without unnecessary pipeline complexity
- Transforming MEDS-style clinical events and CT image paths into a unified object schema preserving temporal alignment and label correctness for survival modeling
- Packaging with model weights and documentation for secure academic environments with strict dependency management

**3. LLM Benchmarking for Clinical Trial Matching**
- Built benchmarking framework for evaluating trial-matching performance across direct LLM inference and embedding-based classifiers
- Implemented vLLM/OpenAI-compatible evaluation runners, configurable prompt/filter modes, concurrent sample evaluation with timeout/skip handling, and standardized experiment outputs
- Added embedding pipelines with logistic regression/MLP/transformer heads, k-fold and stratified-split evaluation, automatic threshold tuning (F-beta/Youden's J), and detailed reporting (accuracy/F1/AUC, per-class metrics, confusion matrices, latency profiling)
- Generated clinical trial matching evaluation benchmarks using EHRSHOT

Key challenges solved:
- Which model families and scales achieve the best accuracy-generalization-efficiency tradeoff on clinical text for inclusion/exclusion criterion matching
- How document filtering strategy, number of notes, and pooling approach affect matching performance and robustness
- Whether criterion-level decisions should be aggregated vs. optimizing trial-level predictions directly from embeddings
- Transfer reliability of classifier heads from synthetic to real-world data

Other contributions:
- Facilitated a data-for-equity deal with MSKCC to obtain multi-modal data
- Contributed to JEPA-based architecture pushing SoTA in biomedical foundation models for next-event prediction
- Automated application of RECIST criteria to evaluate tumor progression from 2 timepoints

### Memorial Sloan Kettering Cancer Center — Machine Learning Engineer / Data Analyst
March 2021 to May 2025 | New York, NY
Supervisor: Andrew Vickers

- Engineered data pipelines with SQL-extracted institutional data and wrote statistical code for Amplio (https://www.mskcc.org/amplio-system), allowing sarcoma, melanoma, whipple, gastrectomy, and liver surgeons to see patient outcomes
- Developed AI radiology tool with Llama 3.1:70B, trained SAM image segmentation models and built RShiny dashboard
- Led statistical analyses for a landmark study on post-chemotherapy RPLND policies in testicular cancer, applying GAM, logistic regression, Kaplan-Meier, CoxPH, and DCA to inform surgeon decisions (https://pubmed.ncbi.nlm.nih.gov/40073938/)
- Developed dcurves Python package for Decision Curve Analysis (29k+ downloads on PyPI at time of writing — see live figure on `site/resume.html`); maintained instructional website decisioncurveanalysis.org
- Developed llmtag Python package for clinical data labeling with local LLMs; redesigned CLI, optimized labeling algorithms
- Engineered Llama3.1:70B + RAG text-to-SQL pipeline (no-more-sql) using Streamlit and FAISS; served 50+ Data Scientists at MSKCC
- Completed patient comorbidity analysis using survey data with pointblank validation
- Authored R scripts for data cleaning and statistical analyses
- Delivered presentations to 100+ research biostatisticians and developers
- Contributed to publications on prostate cancer and robot-assisted surgery outcomes (Eur Urol Focus 2023, J Robot Surg 2023)

Tools: Python, R, SQL, Docker, Git, Bash, AWS, RShiny, ggplot2, Jupyter Lab
Statistical Methods: GAM, CoxPH, Kaplan-Meier, logistic regression, DCA

### Sema4 — Bioinformatics Intern
February 2020 to February 2021 | Stamford, CT

- Engineered automated pipelines with Bash, Python, WDL, and AWS to detect structural variants in 100+ 100GB+ BAM files using Delly, SvABA, Manta, and Illumina DRAGEN
- Utilized AWS EC2 for genome alignment; processed terabytes of data in S3
- Identified repeat variants in 100+ samples contrasting insulin vs non-insulin pancreatic neuroendocrine tumors (PNETs) for diabetes therapy research
- Visualized results with Circos plots, stacked bar plots, heat maps, and scatter plots using genomic R libraries and ggplot2

Tools: Python, R, AWS (EC2, S3), Git, Docker, Bash, WDL
Bioinformatics: Delly, SvABA, Manta, Illumina DRAGEN

### Rutgers University, Cai Lab — Senior Design Project Lead
September 2018 to June 2019 | Piscataway, NJ

- Designed RNA-seq pipeline to analyze gene expression at multiple timepoints
- Developed MATLAB GUI and K-Means clustering algorithm for time-series gene expression analysis
- Applied OOP principles and Big O calculations for GUI optimization
- Presented project to 150+ peers

Tools: MATLAB, R, Linux, Bash

### SPEX CertiPrep Group LLC — Inorganic Manufacturing Associate
May 2018 to May 2019 | Metuchen, NJ

- Quality assurance, manufacturing, and packaging of inorganic chemical standards
- Wet-lab techniques: pipetting, gravimetry, pH adjustment, filtration, combustion in muffle furnace
- Programmed Hudson automated pipettor robot using SOLOsoft
- Automated manual Excel tasks for weight calculations and data organization

### US Pharma Lab — R&D Intern
June 2017 to July 2017 | North Brunswick, NJ

- Supplement development: granulation, formulations, fluid bed drying, friability testing
- Market research and regulatory document indexing (MSDS, CoA, Vegan, Halal, Kosher certifications)

### Princeton University — Research Assistant
May 2017 to September 2017 | Princeton, NJ

- Developed algorithms in MATLAB and Java to locate self-depurinating sequences in DNA
- Analyzed self-depurination mechanism effects on site-directed mutagenesis

### National Taiwan University, Chen Laboratory — Research Intern
August 2017 | Taipei, Taiwan

- Novel research on mutagenic DNA SDP sites
- Investigated gene NR2B neurological significance
- Laboratory techniques: RNA extraction, RT-PCR, TA Cloning, In Situ Hybridization

### Tokyo Chemical Industry Co., Ltd — Quality Control Intern
June 2016 to July 2016 | Saitama, Japan

- 160 hours training in instrumentation: GC, HPLC, NMR, IR, and wet-lab analysis
- Completed 5+ QA forms/specs daily

## Education

**Icahn School of Medicine at Mount Sinai**
Master's in Biomedical Data Science
Completed: March 2021 | New York, NY

**Rutgers University — School of Engineering, New Brunswick**
Bachelor's in Biomedical Engineering; Major in Chinese
Completed: May 2019 | New Brunswick, NJ
Huayu Enrichment Scholarship — Taiwan Ministry of Education (MOE)

**National Taiwan University**
Certificate in Advanced Chinese
Completed: August 2015 | Taipei, Taiwan
MOE Full Scholarship recipient

## Projects & Notable Achievements

**dcurves Python Library** (August 2021 – Present)
https://decisioncurveanalysis.org | https://github.com/MSKCC-Epi-Bio/dcurves
- Evaluates binary and survival models (live download count on `site/resume.html`)
- Built and maintain instructional website and technical forum
- 20+ methods, 50+ unit tests, international academic/clinical adoption

**llmtag Python Package**
https://github.com/ygivenx/llmtag
- Clinical data labeling with local LLMs
- Redesigned CLI and optimized labeling algorithms

**no-more-sql — LLM Text-to-SQL Project** (March 2024)
https://github.com/juntotechnologies/no-more-sql
- Llama3.1:70B + RAG pipeline with Streamlit and FAISS
- Secure text-to-SQL conversion for MSKCC, serving 50+ Data Scientists

**Statistical Contributions to Landmark Paper** (March 2025)
https://pubmed.ncbi.nlm.nih.gov/40073938/
- All statistical analyses for landmark RPLND study in testicular cancer
- Responsible for all numbers, tables, and figures in the publication

**2024 NYC Marathon** (Mar 2023 – Dec 2024)
https://results.nyrr.org/event/M2024/result/15967
- Ran ~1k miles in 2023, completed NYC 9+1 program for guaranteed entry
- Ran ~1.4k miles in 2024, finished NYC Marathon in 3hr 48m

**2015 Chinese Bridge Competition**
https://www.youtube.com/watch?v=sHFZu_TLaN4
- Competed with ~1.5 years of Mandarin study
- Applied for beginner division, elevated to advanced, placed 3rd

## Skills

**Programming (Proficient, 5+ years):** Python, R, Git, Bash/Zsh, SQL, HTML, CSS, Docker
**Programming (Intermediate):** AWS, MATLAB, Regex, ggplot2, WDL, Poetry, tox, Jupyter Lab
**AI / ML:** LLM fine-tuning, RAG pipelines, multi-agent/swarm orchestration, self-hosted local LLM deployment (vLLM, llama.cpp), LLM evals (promptfoo), SAM image segmentation, JEPA-based architectures, text encoder + MLP models, FAISS, Streamlit
**Statistical Methods:** GAM, CoxPH, Kaplan-Meier, logistic regression, Decision Curve Analysis (DCA), survival analysis, multi-variate analysis
**Bioinformatics:** RNA-seq pipelines, structural variant detection (Delly, SvABA, Manta, DRAGEN), Circos plots, genomic R libraries
**Visualization & Dashboards:** RShiny, ggplot2, Circos, heat maps, scatter plots, stacked bar plots, custom fleet-monitoring dashboards (Glances)

## Languages

- English — Native
- Hindi — Native
- Mandarin Chinese — Fluent (passed into advanced division at Chinese Bridge)
- Japanese — Basic/Conversational
- Spanish — Basic

## Publications

Google Scholar: https://scholar.google.com/citations?hl=en&user=eR7hro0AAAAJ

- Pellegrino F, et al. "Prostate-specific Antigen Density Cutoff of 0.15 ng/ml/cc..." Eur Urol Focus. 2023 Mar;9(2):291-297.
- Pellegrino F, et al. "The effect of the da Vinci® Vessel Sealer on robot-assisted laparoscopic prostatectomy complications." J Robot Surg. 2023 Apr 12.
- Testicular cancer post-chemotherapy RPLND landmark study (2025) — https://pubmed.ncbi.nlm.nih.gov/40073938/
