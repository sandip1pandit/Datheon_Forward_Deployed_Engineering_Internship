# Enterprise Multi-Tenant RAG with Role-Based Access Control (RBAC)

## 1. Project Overview

An enterprise-grade Retrieval-Augmented Generation (RAG) system built using Python, FastAPI, Qdrant, and Large Language Models.

The system allows employees to ask questions about company documents while enforcing strict access control based on:

- Tenant (company)
- Department
- Security clearance level
- User role

It also includes query rewriting, semantic document retrieval, cross-encoder reranking, citation generation, and hallucination guardrails.

## 2. Key Features

### Secure Multi-Tenancy
- Isolates documents belonging to different companies.
- Prevents users from accessing another tenant's documents.
- Applies tenant-based filtering during retrieval.

### Role-Based Access Control
- JWT-based authentication.
- Tenant administrators can access all departments within their own tenant.
- Employees can access documents belonging to their assigned department.

### Clearance-Based Access Control
Supports four clearance levels:

| Level | Clearance |
|---|---|
| 0 | PUBLIC |
| 1 | INTERNAL |
| 2 | CONFIDENTIAL |
| 3 | SECRET |

Users can retrieve documents only when their clearance level is sufficient.

### Advanced RAG Pipeline
- PDF document ingestion and text extraction.
- Text chunking and vector embeddings.
- Semantic search using Qdrant.
- Query rewriting using an LLM.
- Cross-encoder reranking.
- Context-based answer generation.

### Citation and Hallucination Guardrails
- Generates answers using retrieved document evidence.
- Includes source document and page-number citations.
- Abstains when sufficient evidence is unavailable.
- Validates citation indices before returning answers.

## 3. Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python 3.12 |
| API Framework | FastAPI |
| Vector Database | Qdrant |
| Embeddings | Sentence Transformers |
| Reranking | Cross-Encoder |
| LLM Provider | Groq |
| Authentication | JWT |
| Password Hashing | Argon2 |
| PDF Processing | PyPDF |
| Testing | Pytest |

## 4. Project Architecture

```text
TASK2/
│
├── config/
├── data/
│   ├── raw/
│   │   └── pdf/
│   ├── qdrant/
│   └── users.db
│
├── src/
│   ├── api.py
│   ├── models.py
│   ├── security.py
│   ├── user_store.py
│   ├── pipeline.py
│   │
│   ├── ingestion/
│   │   └── pdf.py
│   │
│   ├── retrieval/
│   │   └── search.py
│   │
│   ├── generation/
│   │   ├── answer_generator.py
│   │   └