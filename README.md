# 🌱 EcoMind AI

### Evidence-Grounded Biodiversity Intelligence & Multi-Metric Environmental Reasoning

EcoMind AI is an evidence-grounded environmental intelligence system designed to help users understand interactions between **soil health, climate and water availability, land use, biodiversity, and human pressures**.

Instead of generating generic environmental advice, EcoMind converts user input into a structured environmental state, identifies interacting ecological stressors, reasons across multiple environmental metrics, retrieves relevant scientific evidence using **RAG + ChromaDB**, and produces traceable recommendations with supporting evidence.

---

## 🎯 Problem

Environmental conditions are interconnected.

For example:

- Low rainfall can increase water stress.
- Low soil organic carbon can affect soil resilience.
- Continuous monoculture can reduce ecological diversity.
- Pesticide pressure can affect beneficial insects and pollinators.
- Habitat disturbance can increase biodiversity pressure.

A recommendation based on only one environmental variable can therefore miss important ecological relationships.

EcoMind AI addresses this through **multi-metric ecological reasoning combined with scientific evidence retrieval**.

---

# 💡 Solution

EcoMind AI follows an evidence-grounded reasoning pipeline:

```text
User Input
    ↓
Environmental State Extraction
    ↓
Input Completeness Check
    ↓
Clarifying Questions
    ↓
Multi-Metric Stressor Detection
    ↓
Cross-Variable Ecological Reasoning
    ↓
Scientific RAG Retrieval
    ↓
Metadata Filtering
    ↓
Hybrid Evidence Reranking
    ↓
Claim Safety Validation
    ↓
Evidence-Grounded Recommendations
    ↓
Reasoning & Retrieval Trace
````

The system makes the reasoning and evidence trail inspectable rather than hiding the process behind a generic chatbot response.

---

# 🧠 Core Capabilities

## 1. Environmental State Extraction

EcoMind extracts environmental information from natural-language and structured input.

### 🌱 Soil

* Soil Organic Carbon (SOC)
* Soil pH
* Soil moisture
* Soil texture

### 🌦️ Climate & Hydrology

* Rainfall
* Drought conditions
* Water availability
* Temperature

### 🌾 Land & Crop System

* Crop type
* Monoculture
* Mixed cropping
* Agroforestry
* Land-use characteristics

### 🐝 Biodiversity

* Pollinator presence
* Species richness
* Habitat diversity
* Ecological indicators

### ⚠️ Human / Ecological Pressure

* Pesticide pressure
* Water extraction
* Habitat disturbance
* Other environmental pressures

---

# 🔗 Multi-Metric Ecological Reasoning

EcoMind does not treat environmental variables independently.

The reasoning engine identifies relationships between multiple environmental domains.

Example:

```text
Low Soil Organic Carbon
        +
Low Rainfall
        ↓
Reduced Soil & Water Resilience
```

Another example:

```text
Monoculture
      +
Low Habitat Diversity
      ↓
Biodiversity Pressure
```

Another:

```text
Pesticide Pressure
      +
Low Floral Resources
      ↓
Pollinator Vulnerability
```

These relationships are used to generate intervention strategies that address interacting environmental pressures.

---

# 📚 Scientific RAG Knowledge System

Scientific grounding is a core component of EcoMind AI.

The knowledge system organizes environmental and biodiversity evidence around:

* Soil health
* Climate and water
* Land use
* Biodiversity
* Human environmental pressures
* Ecological interventions

The retrieval pipeline uses:

```text
User Query
    ↓
Query Embedding
    ↓
ChromaDB Vector Search
    ↓
Semantic Similarity
    ↓
Metadata Filtering
    ↓
Hybrid Evidence Reranking
    ↓
Evidence Chunks
```

The hybrid ranking process combines semantic similarity with additional relevance signals including:

* Environmental metric overlap
* Region/context alignment
* Lexical relevance

Retrieved evidence is then passed through claim-safety validation before being used to support recommendations.

---

# 🔍 Retrieval Trace

EcoMind exposes the retrieval process to the user.

Evidence retrieval can expose:

* Retrieved evidence
* Relevance score
* Environmental metric
* Region/context
* Publication information
* Evidence passage
* Source/institutional record
* Retrieval and reranking information

This allows users and evaluators to inspect **why evidence was retrieved and how it contributed to the recommendation**.

---

# 🛡️ Claim Safety

EcoMind includes a claim-safety layer designed to reduce unsupported scientific claims.

The system avoids presenting unsupported numerical predictions as guaranteed outcomes.

Quantitative information is treated as **literature-reported evidence ranges** when applicable rather than automatically treating it as a site-specific prediction.

Conceptually:

```text
Literature-Reported Range
        ↓
Referenced Scientific Evidence
        ↓
Context / Conditions
        ↓
EcoMind Interpretation
```

Environmental outcomes vary by local conditions, so evidence-derived ranges should not be interpreted as guaranteed results for a specific site.

---

# 💬 Conversational Intelligence

EcoMind supports incomplete and multi-turn environmental conversations.

If critical information is missing, the system asks targeted clarifying questions instead of inventing values.

### Example

**User:**

> My farm receives very little rainfall and experiences frequent drought. I grow crops every year but I don't have soil test results.

EcoMind can request information such as:

* Geographic/agro-climatic region
* Primary crop
* Farming system
* Available soil information

The system can then incorporate the additional information into subsequent reasoning.

---

# 🧪 Official Benchmark Scenario

EcoMind includes a benchmark scenario based on the challenge specification.

### Benchmark Inputs

```text
Region: Semi-arid Karnataka
Soil Organic Carbon: 0.30%
Rainfall: Low
Crop: Wheat
Farming System: Monoculture
```

The benchmark tests whether EcoMind can identify interacting environmental stressors and generate evidence-grounded intervention strategies.

The reasoning considers relationships involving:

* Soil carbon
* Water/rainfall stress
* Crop-system diversity
* Biodiversity
* Ecological resilience

---

# 📊 Multi-Metric Scenario Simulator

EcoMind includes a deterministic scenario simulator for exploring environmental interventions.

The simulator allows users to inspect:

* Environmental conditions
* Active stressors
* Cross-variable ecological couplings
* Candidate interventions
* Impacted metrics
* Time horizon
* Confidence
* Reasoning trace

### Important

Simulator outputs are intended as **illustrative, literature-informed scenario estimates**, not physical models or guaranteed site-specific environmental predictions.

---

# 🗂️ Scientific Knowledge Explorer

EcoMind provides a dedicated interface for exploring the scientific knowledge corpus.

Users can inspect:

* Knowledge documents
* Retrieved evidence
* Relevance
* Environmental metrics
* Publication information
* Institutional sources
* Retrieval traces

This makes the RAG layer visible and auditable.

---

# 📤 Audit Dossier

EcoMind can export an audit dossier containing information such as:

* Environmental input
* Extracted environmental state
* Detected stressors
* Ecological couplings
* Recommendations
* Impacted metrics
* Evidence
* Sources
* Reasoning/retrieval trace

The dossier provides a structured record of how an environmental recommendation was generated.

---

# 🏗️ System Architecture

```text
                         ┌──────────────────────┐
                         │       React UI       │
                         │                      │
                         │  Diagnostic Chat     │
                         │  Land Dashboard      │
                         │  Simulator            │
                         │  RAG Explorer         │
                         │  Benchmark            │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Express Server    │
                         │        :3000         │
                         │                      │
                         │ Frontend Hosting     │
                         │ API Proxy             │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI API     │
                         │        :8001         │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     Orchestrator     │
                         └──────────┬───────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
      State Extractor       Clarification Engine      Conversation
                                                            Memory
             │
             ▼
      Multi-Metric Reasoning
             │
             ▼
         RAG Service
             │
             ▼
          ChromaDB
             │
             ▼
     Scientific Knowledge
           Corpus
             │
             ▼
        Claim Safety
             │
             ▼
    Recommendation Engine
```

---

# 🛠️ Technology Stack

## Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* SQLite
* ChromaDB
* ONNX Runtime
* Scientific RAG pipeline

## Frontend

* React
* TypeScript
* Vite
* Tailwind CSS
* Recharts
* Motion
* React Markdown

## Server

* Node.js
* Express

## Testing & Development

* Pytest
* TypeScript
* Vite production build
* Git
* GitHub

---

# 📁 Project Structure

```text
Eco-Mind-AI/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── reasoning/
│   │   ├── rag/
│   │   └── main.py
│   │
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── components/
│   ├── pages/
│   ├── services/
│   └── ...
│
├── public/
├── scripts/
├── package.json
├── vite.config.ts
├── server.ts
├── README.md
└── .gitignore
```

---

# 🗄️ Data & Knowledge Architecture

EcoMind uses complementary structured and vector data layers.

## Relational Data

SQLite + SQLAlchemy are used for application-level structured information such as:

* Land/farm profiles
* Environmental states
* Conversations
* User/session information
* Application records

## Vector Knowledge

ChromaDB is used for semantic retrieval of scientific environmental evidence.

The knowledge workflow is:

```text
Scientific Document
        ↓
Knowledge Preparation
        ↓
Document Chunks
        ↓
Embeddings
        ↓
ChromaDB
        ↓
Semantic Retrieval
        ↓
Metadata Filtering
        ↓
Hybrid Reranking
        ↓
Evidence
```

---

# 🔌 API Overview

The application exposes backend APIs through the Express proxy.

Core endpoints include:

```text
GET  /api/health
GET  /api/land-profiles
POST /api/land-profiles
POST /api/chat
```

The health endpoint can be used to check backend availability and vector knowledge-system status.

---

# 🚀 Local Setup

## Prerequisites

Install:

* Python 3.11+
* Node.js 20+
* npm

---

## 1. Clone the Repository

```bash
git clone https://github.com/prajwal12smp-cpu/Eco-Mind-AI.git

cd Eco-Mind-AI
```

---

## 2. Create Python Environment

### Windows

```powershell
python -m venv .venv

.venv\Scripts\activate
```

### Linux/macOS

```bash
python3 -m venv .venv

source .venv/bin/activate
```

---

## 3. Install Backend Dependencies

```bash
pip install -r backend/requirements.txt
```

---

## 4. Install Frontend Dependencies

```bash
npm install
```

---

## 5. Start the Development Server

```bash
npm run dev
```

The application is normally available at:

```text
http://localhost:3000
```

The FastAPI backend runs internally on:

```text
http://localhost:8001
```

---

# 🧪 Running Tests

Run the backend test suite:

```bash
PYTHONPATH=. pytest -q
```

### Windows PowerShell

```powershell
$env:PYTHONPATH="."
pytest -q
```

The current verified test suite contains:

```text
23 tests
23 passed
0 failed
```

---

# 🏭 Production Build

Build the frontend:

```bash
npm run build
```

Start the production server:

```bash
node dist/server.cjs
```

The production build should be tested using the same benchmark and API flows as the development environment.

---

# 🔬 Example Query

### Input

```text
I manage a wheat farm in semi-arid Karnataka.
Soil organic carbon is 0.3%, rainfall is low,
and wheat is grown continuously as a monoculture.
What interventions should I consider?
```

### EcoMind Processing

```text
Environmental State
        ↓
Low SOC
Low rainfall
Wheat monoculture
        ↓
Stressors
        ↓
Cross-variable ecological couplings
        ↓
Candidate interventions
        ↓
Scientific RAG
        ↓
Evidence validation
        ↓
Traceable recommendation
```

The final response can include:

* Recommended intervention
* Scientific rationale
* Impacted metrics
* Time horizon
* Confidence
* Supporting evidence
* Retrieval/reasoning trace

---

# 🎯 Darukaa.Earth Challenge Alignment

EcoMind AI was designed around the requirements of the **Darukaa.Earth AI Biodiversity Intelligence Chatbot Challenge**.

| Challenge Requirement              | EcoMind Implementation                          |
| ---------------------------------- | ----------------------------------------------- |
| Structured environmental knowledge | Environmental state model                       |
| Soil health                        | SOC, pH, moisture, texture                      |
| Climate factors                    | Rainfall, drought, temperature                  |
| Land use                           | Crop system, monoculture, diversity             |
| Biodiversity                       | Pollinator and habitat indicators               |
| Human impact                       | Pesticide and environmental pressure indicators |
| RAG                                | ChromaDB semantic retrieval                     |
| Scientific grounding               | Scientific knowledge corpus                     |
| Retrieval transparency             | Retrieval trace                                 |
| Incomplete input                   | Clarifying question engine                      |
| Multi-turn conversation            | Conversation context                            |
| Multi-metric reasoning             | Cross-variable ecological reasoning             |
| Evidence-backed recommendations    | Recommendation + evidence                       |
| Impacted metrics                   | Structured recommendation output                |
| Time horizon                       | Recommendation metadata                         |
| Confidence                         | Recommendation metadata                         |
| Benchmark scenario                 | Semi-arid Karnataka case                        |
| Structured input                   | JSON/environmental state support                |

---

# 📈 Evaluation-Oriented Design

EcoMind was designed around the major evaluation areas of the challenge.

## Reasoning

Cross-variable environmental interactions are explicitly modeled.

## Scientific Grounding

Recommendations are connected to retrieved scientific evidence.

## Knowledge System Design

Structured environmental state and vector knowledge retrieval are combined.

## Conversational Intelligence

The system handles incomplete inputs and multi-turn context.

## Output Clarity

Recommendations expose:

* Action
* Scientific rationale
* Impacted metrics
* Time horizon
* Confidence
* Evidence

---

# 🧪 Testing Strategy

The project includes automated tests covering major backend components including:

* API behavior
* Database operations
* Environmental state extraction
* Multi-metric reasoning
* Ecological couplings
* RAG retrieval
* Claim safety
* Structured inputs
* Error handling

Additional manual QA scenarios include:

* Official benchmark case
* Sparse-data clarification
* Multi-turn memory
* Context updates
* Unsupported numerical claims
* Prompt-injection resistance
* RAG relevance
* Scientific source-link validation
* Simulator behavior
* Audit dossier generation

---

# 🔐 Security

The project follows basic application security practices including:

* Environment-variable configuration
* No committed production secrets
* Pydantic input validation
* SQLAlchemy ORM
* Structured API validation
* Controlled file/path handling
* Graceful application shutdown

For production deployment, additional infrastructure-level security controls should be applied.

---

# ⚠️ Limitations

EcoMind AI is a decision-support and research prototype.

It is not a replacement for:

* Professional agronomic advice
* Laboratory soil testing
* Field biodiversity surveys
* Hydrological modelling
* Site-specific ecological assessments

Environmental outcomes vary according to:

* Soil type
* Climate
* Geography
* Crop
* Management practices
* Seasonal conditions
* Local ecosystem characteristics

Quantitative values should therefore be interpreted as **literature-reported or illustrative evidence ranges where explicitly indicated**, not guaranteed site-specific outcomes.

---

# 📸 Screenshots


### Diagnostic Chat

<img width="947" height="564" alt="Dashboard" src="https://github.com/user-attachments/assets/590ff92c-8ed3-46e0-9bf4-dda0d3604597" />


### Land Dashboard

<img width="949" height="563" alt="Dashboard 1" src="https://github.com/user-attachments/assets/6c9605dd-d090-43e0-ae85-f98b1629a3c6" />


<img width="950" height="563" alt="Dashboard 2" src="https://github.com/user-attachments/assets/d9960e1b-e814-415f-8d10-6de4b7e32ced" />


### Multi-Metric Simulator

<img width="959" height="565" alt="Dashboard 3" src="https://github.com/user-attachments/assets/72caa3c2-2d67-4936-8ec1-b6b102b2d9ae" />


### Scientific RAG Explorer

<img width="949" height="564" alt="Dashboard 4" src="https://github.com/user-attachments/assets/f5fae0e0-3369-46bc-9313-5a6558f10b93" />


### Demo Video






# 🌍 Project Vision

EcoMind AI aims to make environmental intelligence more:

* Evidence-grounded
* Explainable
* Multi-dimensional
* Auditable
* Accessible through natural language

The core idea is:

> **Environmental recommendations should consider not only what is happening, but also how different ecological variables interact and what scientific evidence supports the proposed action.**

---

# 👨‍💻 Author

**Prajwal Shivashimpar**

Computer Science & Engineering (AI & ML)

GitHub: **https://github.com/prajwal12smp-cpu/Eco-Mind-AI**

---

# ⭐ Acknowledgements

Built as part of the **Darukaa.Earth AI Biodiversity Intelligence Chatbot Challenge**.

Scientific and environmental knowledge is attributed to the respective research institutions, publications, and organisations represented in the project's knowledge corpus.
