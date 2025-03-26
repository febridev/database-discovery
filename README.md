# Database Discovery

Database Internal Tools For Automation Operations

## Pre-requisites

- Python 3.12+
- [Package Manager PDM 2.11+] (https://pdm-project.org/latest/)

## Installation PDM

```bash
brew install pdm
```

Installation Reference to [PDM](https://pdm-project.org/latest/)

## Setup Project For Development

### GIT Clone SSH

```bash
git clone git@git.aladinbank.id:engineering/dbops.git
```

### Install Dependencies

```bash
cd dbops/db_automation/database_platform/database_discovery
pdm install
```

### Setup env

```bash
cp env.example .env
```

Update variable on .env with configuration for your project

### Run All Module

```bash
pdm run python -m database_discovery

```

### Run Specific Module

```bash
pdm run python -m database_discovery.v1.scrap_service.project_service.project
```
