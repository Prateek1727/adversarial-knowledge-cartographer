# ADR 001: Why LangGraph for Multi-Agent Orchestration

**Status:** Accepted  
**Date:** 2025-01-08  
**Deciders:** Core Team  

## Context

We needed a framework to orchestrate multiple AI agents (Scout, Mapper, Adversary, Judge, Synthesis) in a complex workflow with:
- Conditional branching based on iteration count
- State management across agent transitions
- Checkpointing for long-running research tasks
- Clear visualization of agent flow

## Decision

We chose **LangGraph** over alternatives like LangChain LCEL, CrewAI, or custom orchestration.

## Rationale

### Why LangGraph?

1. **Graph-Based State Management**
   - Natural representation of multi-agent workflows as directed graphs
   - Built-in state persistence with checkpointing
   - Clear visualization of agent transitions

2. **Conditional Logic Support**
   - Native support for conditional edges (e.g., "continue iterating or synthesize?")
   - Easy to implement adversarial loops with iteration limits

3. **LangChain Integration**
   - Seamless integration with LangChain LLMs and tools
   - Access to entire LangChain ecosystem (Groq, OpenAI, Anthropic)

4. **Production-Ready Features**
   - Built-in checkpointing for fault tolerance
   - State inspection for debugging
   - Async execution support

### Alternatives Considered

- **LangChain LCEL**: Too linear, difficult to implement conditional loops
- **CrewAI**: Higher-level abstraction, less control over agent flow
- **Custom Orchestration**: More work, reinventing the wheel

## Consequences

### Positive
- Clear, maintainable agent workflow code
- Easy to add new agents or modify flow
- Built-in fault tolerance with checkpoints
- Strong community support

### Negative
- Learning curve for team members unfamiliar with LangGraph
- Dependency on LangChain ecosystem
- Graph complexity can grow with more agents

## Implementation

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(WorkflowState)
workflow.add_node("scout", scout_agent)
workflow.add_node("mapper", mapper_agent)
workflow.add_node("adversary", adversary_agent)
workflow.add_node("judge", judge_agent)
workflow.add_node("synthesis", synthesis_agent)

workflow.add_conditional_edges(
    "judge",
    should_continue,
    {
        "continue": "scout",
        "synthesize": "synthesis"
    }
)
```

## References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Multi-Agent Systems with LangGraph](https://blog.langchain.dev/langgraph-multi-agent-workflows/)
