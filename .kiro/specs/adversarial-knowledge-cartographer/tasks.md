# Implementation Plan

- [x] 1. Set up project structure and dependencies
  - Create Python project with virtual environment
  - Install core dependencies: LangGraph, LangChain, Pydantic, FastAPI
  - Install search and extraction libraries: httpx, beautifulsoup4, trafilatura
  - Install testing frameworks: pytest, hypothesis, pytest-mock
  - Set up project directory structure: agents/, models/, utils/, tests/
  - Create configuration management for API keys and settings
  - _Requirements: All requirements depend on proper setup_

- [x] 2. Implement core data models
- [x] 2.1 Create Pydantic models for workflow state and data structures
  - Implement Source model with url, title, content, domain, retrieved_at fields
  - Implement Relationship model with source, relation, target, citation, credibility fields
  - Implement Conflict model with point_of_contention, side_a, side_b, citations
  - Implement KnowledgeGraph model with entities, relationships, conflicts
  - Implement WorkflowState model with topic, iteration, sources, knowledge_graph, queries
  - Implement CredibilityScore model with domain_authority, citation_indicators, recency
  - _Requirements: 3.5, 8.1, 8.2, 8.3, 8.4_

- [x] 2.2 Write property test for data model validation
  - **Property 8: Knowledge graph JSON validity**
  - **Property 22: Entity uniqueness in graph**
  - **Property 23: Relationship field completeness**
  - **Property 24: Conflict field completeness**
  - **Validates: Requirements 3.5, 8.1, 8.2, 8.3, 8.4**

- [x] 2.3 Write property test for referential integrity
  - **Property 27: Referential integrity**
  - **Validates: Requirements 11.5**

- [x] 3. Implement workflow orchestration with LangGraph
- [x] 3.1 Create LangGraph state machine structure
  - Define workflow graph with nodes for Scout, Mapper, Adversary, Judge, Synthesis
  - Implement state transitions between agents
  - Add conditional edges for iteration logic (weak claims → loop back)
  - Add termination conditions (max 3 iterations or sufficient evidence)
  - _Requirements: 1.1, 1.3, 2.5, 6.1, 6.3, 6.4_

- [x] 3.2 Implement workflow initialization and topic validation
  - Create workflow entry point that accepts topic string
  - Validate topic is non-empty and contains meaningful content
  - Initialize WorkflowState with validated topic
  - Emit status message on successful initialization
  - _Requirements: 1.1, 1.2, 1.4_

- [x] 3.3 Write property tests for workflow initialization
  - **Property 1: Workflow initialization with valid topics**
  - **Property 2: Invalid topic rejection**
  - **Validates: Requirements 1.1, 1.2, 1.3, 1.4**

- [x] 3.4 Write property test for iteration limits
  - **Property 17: Maximum iteration limit**
  - **Validates: Requirements 6.4**

- [x] 4. Implement Scout Agent
- [x] 4.1 Create search API integration
  - Implement Tavily API client with error handling
  - Add fallback to Serper API if Tavily fails
  - Implement query execution with diversity mode
  - Add rate limiting and exponential backoff logic
  - _Requirements: 2.1, 10.1, 10.4_

- [x] 4.2 Implement content extraction from search results
  - Use trafilatura to extract clean text from HTML
  - Extract title, URL, domain from search results
  - Handle extraction failures gracefully (log and skip)
  - Filter out paywalled or inaccessible content
  - _Requirements: 2.3, 2.4_

- [x] 4.3 Implement source collection and validation
  - Collect minimum 10 sources with unique domains
  - Create Source objects with all required fields
  - Validate source completeness before adding to state
  - _Requirements: 2.2, 2.3_

- [x] 4.4 Write property tests for Scout agent
  - **Property 3: Scout phase source diversity**
  - **Property 4: Source completeness**
  - **Property 5: Scout to Mapper state transition**
  - **Validates: Requirements 2.2, 2.3, 2.5**

- [x] 4.5 Write unit tests for error handling
  - Test search API failure recovery
  - Test content extraction failure handling
  - _Requirements: 2.4, 10.1, 10.2_

- [x] 5. Implement Mapper Agent
- [x] 5.1 Create Mapper prompt and LLM integration
  - Implement Mapper system prompt with JSON schema
  - Configure LLM with structured output mode (function calling)
  - Add retry logic for malformed JSON responses
  - _Requirements: 3.1, 3.2, 10.3, 11.1, 11.2_

- [x] 5.2 Implement entity extraction and deduplication
  - Extract entities from LLM response
  - Implement fuzzy matching for entity deduplication (edit distance < 3)
  - Maintain unique entity list
  - _Requirements: 3.1, 11.4_

- [x] 5.3 Implement relationship extraction with citations
  - Extract Knowledge Triplets from LLM response
  - Ensure each relationship has source, relation, target, citation
  - Validate citation references valid source URLs
  - _Requirements: 3.2, 3.3_

- [x] 5.4 Implement conflict detection
  - Extract conflicts from LLM response
  - Ensure conflicts have all required fields (point_of_contention, sides, citations)
  - _Requirements: 3.4_

- [x] 5.5 Build and validate Knowledge Graph output
  - Assemble KnowledgeGraph from entities, relationships, conflicts
  - Validate referential integrity (relationships reference existing entities)
  - Serialize to JSON and validate against schema
  - _Requirements: 3.5, 11.5_

- [x] 5.6 Write property tests for Mapper agent
  - **Property 6: Mapper entity extraction**
  - **Property 7: Relationship citation completeness**
  - **Property 25: Structured output enforcement**
  - **Property 26: Entity deduplication**
  - **Validates: Requirements 3.1, 3.3, 11.1, 11.2, 11.4**

- [x] 5.7 Write unit test for conflict detection
  - Test with sources containing known contradictions
  - _Requirements: 3.4_

- [x] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement Adversary Agent
- [x] 7.1 Create Adversary prompt and weakness analysis
  - Implement Adversary system prompt for red-teaming
  - Configure LLM to identify single-source claims
  - Detect outdated sources (> 2 years old)
  - Identify potential bias indicators
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 7.2 Implement adversarial query generation
  - Generate minimum 3 counter-evidence queries
  - Ensure queries are designed to debunk current findings
  - Format queries for search API
  - _Requirements: 4.4_

- [x] 7.3 Implement query execution and graph updates
  - Execute adversarial queries through Scout agent
  - Integrate counter-evidence into existing Knowledge Graph
  - Maintain state across iterations
  - _Requirements: 4.5, 4.6, 6.2_

- [x] 7.4 Implement query deduplication
  - Track executed queries in WorkflowState
  - Prevent duplicate query execution
  - _Requirements: 6.5_

- [x] 7.5 Write property tests for Adversary agent
  - **Property 9: Single-source weakness detection**
  - **Property 10: Outdated source detection**
  - **Property 11: Adversarial query generation**
  - **Property 12: Counter-evidence integration**
  - **Property 16: Iteration state preservation**
  - **Property 18: Query deduplication**
  - **Validates: Requirements 4.1, 4.2, 4.4, 4.6, 6.2, 6.5**

- [x] 7.6 Write unit test for bias detection
  - Test with sources containing known bias patterns
  - _Requirements: 4.3_

- [x] 8. Implement Judge Agent
- [x] 8.1 Implement credibility scoring system
  - Calculate domain authority scores (.edu=1.0, .gov=1.0, .org=0.8, .com=0.5-0.7)
  - Assess citation indicators (references, academic formatting, author credentials)
  - Calculate recency scores based on publication date
  - Compute weighted overall credibility score
  - _Requirements: 5.1, 5.2_

- [x] 8.2 Implement credibility score normalization and validation
  - Ensure all scores are between 0.0 and 1.0
  - Apply weighted average formula (domain 40%, citations 30%, recency 30%)
  - _Requirements: 5.3_

- [x] 8.3 Annotate Knowledge Graph with credibility scores
  - Add credibility scores to each relationship
  - Add credibility scores to conflict sides
  - _Requirements: 5.5_

- [x] 8.4 Implement conflict resolution logic
  - Compare credibility scores for conflicting claims
  - Determine which side has stronger support
  - _Requirements: 5.4_

- [x] 8.5 Write property tests for Judge agent
  - **Property 13: Credibility score normalization**
  - **Property 14: Credibility annotation completeness**
  - **Property 15: Conflict resolution by credibility**
  - **Validates: Requirements 5.3, 5.4, 5.5**

- [x] 8.6 Write unit tests for credibility calculation
  - Test domain authority scoring
  - Test citation indicator assessment
  - Test recency scoring
  - _Requirements: 5.1, 5.2_

- [x] 9. Implement Synthesis Agent
- [x] 9.1 Create Synthesis prompt and report structure
  - Implement Synthesis system prompt for Principal Investigator role
  - Define report structure: Consensus, Battleground, Verdict, Graph
  - _Requirements: 7.5_

- [x] 9.2 Implement consensus identification
  - Analyze Knowledge Graph to find claims with 90%+ source agreement
  - Extract consensus points into report section
  - _Requirements: 7.1_

- [x] 9.3 Implement battleground analysis
  - Extract conflicts from Knowledge Graph
  - Include conflicting claims in battleground section
  - _Requirements: 7.2_

- [x] 9.4 Implement verdict generation
  - Use credibility scores to determine likely correct claims
  - Generate verdicts for each battleground topic
  - _Requirements: 7.4_

- [x] 9.5 Append Knowledge Graph JSON to report
  - Serialize final Knowledge Graph to JSON
  - Validate JSON is parseable
  - Append to end of synthesis report
  - _Requirements: 7.6, 8.5_

- [x] 9.6 Write property tests for Synthesis agent
  - **Property 19: Consensus identification**
  - **Property 20: Battleground extraction**
  - **Property 21: Report structure completeness**
  - **Validates: Requirements 7.1, 7.2, 7.5, 7.6**

- [x] 10. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Implement error handling and logging
- [x] 11.1 Add comprehensive error handling
  - Implement exponential backoff for rate limits
  - Add graceful degradation for partial data
  - Implement state recovery from checkpoints
  - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [x] 11.2 Implement structured logging
  - Add DEBUG logs for agent transitions and entity extraction
  - Add INFO logs for phase completions and source counts
  - Add WARNING logs for data quality issues and fallbacks
  - Add ERROR logs for unrecoverable failures
  - _Requirements: 10.5_

- [x] 11.3 Write unit tests for error handling
  - Test exponential backoff logic
  - Test graceful degradation with partial data
  - Test error message formatting
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 12. Implement API backend with FastAPI
- [x] 12.1 Create FastAPI application structure
  - Set up FastAPI app with CORS middleware
  - Create endpoints for workflow execution
  - Add endpoint for retrieving research session status
  - Add endpoint for retrieving Knowledge Graph JSON
  - _Requirements: 8.1, 8.5_

- [x] 12.2 Implement workflow execution endpoint
  - POST /api/research endpoint accepting topic
  - Execute workflow asynchronously
  - Return session ID for status tracking
  - _Requirements: 1.1_

- [x] 12.3 Implement graph retrieval endpoint
  - GET /api/research/{session_id}/graph endpoint
  - Transform Knowledge Graph to visualization format (nodes, edges)
  - Return JSON with nodes and edges arrays
  - _Requirements: 9.1_

- [x] 12.4 Write integration tests for API endpoints
  - Test workflow execution endpoint
  - Test graph retrieval endpoint
  - Test error responses
  - _Requirements: 1.1, 9.1_

- [x] 13. Implement visualization frontend
- [x] 13.1 Set up React application with React Flow
  - Create React app with TypeScript
  - Install React Flow library
  - Set up component structure
  - _Requirements: 9.1_

- [x] 13.2 Implement graph visualization component
  - Transform API data to React Flow nodes and edges
  - Render entities as nodes with distinct styling
  - Render relationships as directed edges with labels
  - Highlight conflicts with distinct visual indicators
  - _Requirements: 9.2, 9.3, 9.4_

- [x] 13.3 Implement interactive features
  - Add click handlers for nodes to display details
  - Show citations and credibility scores in detail panel
  - Add zoom and pan controls
  - _Requirements: 9.5_

- [x] 13.4 Write unit tests for visualization components
  - Test node rendering
  - Test edge rendering
  - Test click handler registration
  - _Requirements: 9.5_

- [x] 14. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 15. Create documentation and examples
  - Write README with project overview and setup instructions
  - Document API endpoints with example requests/responses
  - Create example research topics for testing
  - Document configuration options (API keys, iteration limits)
  - Add architecture diagram to documentation
  - _Requirements: All requirements_

- [x] 16. Implement advanced 3D visualization system
- [x] 16.1 Set up 3D visualization dependencies
  - Install Three.js, React Three Fiber, and Drei libraries
  - Install D3.js for advanced graph algorithms and force simulation
  - Install Recharts for analytics dashboard components
  - Configure TypeScript types for 3D components
  - _Requirements: 12.1, 12.2_

- [x] 16.2 Create 3D graph rendering engine
  - Implement Three.js scene setup with camera, lighting, and controls
  - Create 3D node components with spherical geometry and materials
  - Implement particle trail system for relationship visualization
  - Add physics-based force-directed layout using D3 force simulation
  - _Requirements: 12.1, 12.2, 12.3_

- [x] 16.3 Implement 3D interaction controls
  - Add orbit camera controls with smooth transitions
  - Implement node selection and hover effects in 3D space
  - Create floating information panels with CSS3D transforms
  - Add keyboard shortcuts for camera navigation
  - _Requirements: 12.4, 12.5_

- [x] 16.4 Create real-time filtering system
  - Implement dynamic graph filtering with smooth animations
  - Add filter controls for node types, credibility scores, and relationships
  - Create search functionality for finding specific entities
  - Implement graph layer management (entities, relationships, conflicts)
  - _Requirements: 12.6_

- [x] 16.5 Build analytics dashboard
  - Create interactive charts showing graph metrics (centrality, clustering, etc.)
  - Implement real-time statistics display (node count, edge count, conflicts)
  - Add graph evolution timeline showing research iteration changes
  - Create export functionality for graph data and visualizations
  - _Requirements: 12.7_

- [x] 16.6 Write property tests for 3D visualization
  - **Property 28: 3D visualization mode switching**
  - **Property 29: 3D physics simulation consistency**
  - **Property 30: 3D interaction responsiveness**
  - **Property 31: Real-time filtering consistency**
  - **Property 32: Analytics dashboard data accuracy**
  - **Validates: Requirements 12.1, 12.2, 12.4, 12.6, 12.7**

- [x] 16.7 Write unit tests for 3D components
  - Test 3D scene initialization and cleanup
  - Test node positioning and physics simulation
  - Test filtering and search functionality
  - Test analytics calculations and dashboard updates
  - _Requirements: 12.1, 12.2, 12.6, 12.7_

- [x] 17. Final checkpoint - Ensure all tests pass including 3D features
  - Ensure all tests pass, ask the user if questions arise.

- [x] 18. Project completion and deployment readiness
  - All 32 correctness properties implemented and tested
  - Complete 5-agent workflow (Scout, Mapper, Adversary, Judge, Synthesis) operational
  - Advanced 3D visualization with analytics dashboard fully functional
  - Comprehensive API documentation and beginner's guide created
  - System successfully tested with real-world research topics
  - Production-ready with error handling, logging, and rate limiting
  - _Status: COMPLETE - System is fully operational and ready for production use_
