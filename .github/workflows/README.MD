# Federated Rural OSDK Platform

A comprehensive MBSE-GIS-SD-SNA platform for participatory rural development modeling.

## Quick Start
1. Navigate to `orchestrator/`
2. Copy `.env.example` to `.env` and set passwords
3. Run `docker-compose up -d`
4. Access n8n at http://localhost:5678

## Architecture
- MBSE Core: SysML/Capella models as single source of truth
- n8n Orchestrator: Central workflow automation
- GitHub Actions: CI/CD and automation triggers