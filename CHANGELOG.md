# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-15

### Added
- Initial release of Resume Screening Agent
- Multi-dimensional evaluation system for quantitative finance positions
  - Project experience scoring (30 points)
  - Internship experience scoring (25 points)
  - Tech stack evaluation (25 points)
  - Research experience scoring (20 points)
  - Competition bonus scoring (15 points)
- Intelligent interview question generation
  - 2 basic questions targeting resume specifics
  - 2-3 advanced questions testing deeper understanding
- LangGraph workflow orchestration
  - PDF parsing node
  - Evaluation node
  - Threshold checking node
  - Question generation node
- Pydantic AI agents for structured outputs
  - Resume evaluator agent
  - Question generator agent
- Comprehensive test suite
  - Unit tests for models, nodes, and workflow
  - Integration tests for agent behavior
  - End-to-end tests for complete workflow
- Usage examples and documentation
  - Basic usage example
  - Custom threshold and batch processing example
  - Detailed README with setup instructions
- Configuration management via environment variables
- Support for customizable screening thresholds

### Features
- Async and sync API support
- Detailed scoring with reasoning for each dimension
- Automatic pass/fail determination based on threshold
- Context-aware interview questions based on candidate profile
- Error handling throughout the workflow
- Structured output using Pydantic models

### Technical Stack
- LangGraph for workflow orchestration
- Pydantic AI for structured AI agents
- LangChain for PDF document processing
- OpenAI GPT-4 for language model
- pytest for comprehensive testing
- Black and Ruff for code quality

[0.1.0]: https://github.com/yourusername/resume-agent/releases/tag/v0.1.0
