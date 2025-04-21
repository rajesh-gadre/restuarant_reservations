# Engineering Design Document

## 1. Overview
This document outlines the architecture, data model, API design, technology stack, and deployment strategy for the Restaurant Reservation Call App. It serves as a blueprint for implementation.

## 2. System Architecture

### 2.1 High-Level Components
- Client App (Web PWA)
- API Backend
- Call Service: Twilio Programmable Voice

### 2.2 Architecture Diagram
```
[Client App] <--> [Next.js API]
                    |
                    +-- [Twilio Programmable Voice]
```

## 3. Data Model

No persistence; reservation data handled in-memory only.

## 4. API Design

| Method | Endpoint   | Description                          |
|--------|------------|--------------------------------------|
| POST   | /api/call  | Trigger Twilio call with reservation details |

Schemas: name, phone, time, party_size

## 5. Sequence Flow
1. User fills the form and submits.
2. Client POSTs to `/api/call` with: name, phone, time, party_size.
3. Backend invokes Twilio REST API to call the restaurant and play a TTS message with details.
4. Returns success or error to client.

## 6. Technology Stack

| Layer        | Choice                     | Notes            |
|--------------|----------------------------|------------------|
| Frontend     | Streamlit (Python)         | Simple UI        |
| Backend      | Streamlit (Python, with Flask for webhook) | All-in-one app   |
| Call Service | Twilio Programmable Voice  | TTS call         |
| Hosting      | Streamlit Community Cloud  | Free tier option |

## 7. Non-Functional Requirements
As defined in the PRD:
- Scalability: support growing user base
- Reliability: 99.9% uptime
- Security: encryption in transit & at rest, secure APIs
- UX: responsive and intuitive UI

## 8. Infrastructure & Deployment
- Containerize all services with Docker
- CI/CD pipeline via GitHub Actions
- Terraform for provisioning (AWS VPC, ECS/EB)
- Logging/monitoring via CloudWatch or ELK stack

## 9. Monitoring & Logging
- Centralized logs (CloudWatch, ELK)
- Error tracking (Sentry)
- Metrics (Prometheus/Grafana)

## 10. Open Decisions
- Hosting: Vercel / Netlify / Other? Please confirm deployment target.

---
*Review & confirm hosting choice before implementation.*
