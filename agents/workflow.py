"""
Workflow orchestration using LangGraph for the Adversarial Knowledge Cartographer.

This module implements the state machine that coordinates the Scout, Mapper,
Adversary, Judge, and Synthesis agents through iterative research cycles.
"""

import logging
from typing import Literal, TypedDict, Optional
from langgraph.graph import StateGraph, END
from models.data_models import WorkflowState
from agents.scout import ScoutAgent
from agents.mapper import MapperAgent
from agents.adversary import AdversaryAgent
from agents.judge import JudgeAgent
from agents.synthesis import SynthesisAgent
from utils.error_handling import StateCheckpoint, StateRecoveryError, validate_partial_data
from utils.logging_config import log_agent_transition

logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    """
    Orchestrates the multi-agent research workflow using LangGraph.
    
    The workflow follows this pattern:
    1. Initialize with topic validation
    2. Scout: Gather diverse sources
    3. Mapper: Extract entities, relationships, conflicts
    4. Adversary: Identify weaknesses and generate counter-queries
    5. Decision: Loop back to Scout if weak claims found (max 3 iterations)
    6. Judge: Evaluate credibility and weight claims
    7. Synthesis: Generate final report with argument topology
    """
    
    def __init__(
        self,
        max_iterations: int = 3,
        scout_agent=None,
        mapper_agent=None,
        adversary_agent=None,
        judge_agent=None,
        synthesis_agent=None,
        enable_checkpoints: bool = True,
        checkpoint_dir: str = ".checkpoints"
    ):
        """
        Initialize the workflow orchestrator.
        
        Args:
            max_iterations: Maximum number of Scout-Mapper-Adversary cycles
            scout_agent: Optional pre-configured Scout agent (for testing)
            mapper_agent: Optional pre-configured Mapper agent (for testing)
            adversary_agent: Optional pre-configured Adversary agent (for testing)
            judge_agent: Optional pre-configured Judge agent (for testing)
            synthesis_agent: Optional pre-configured Synthesis agent (for testing)
            enable_checkpoints: Whether to enable state checkpointing
            checkpoint_dir: Directory for storing checkpoints
        """
        self.max_iterations = max_iterations
        self.scout_agent = scout_agent if scout_agent is not None else ScoutAgent()
        self.mapper_agent = mapper_agent if mapper_agent is not None else MapperAgent()
        self.adversary_agent = adversary_agent if adversary_agent is not None else AdversaryAgent()
        self.judge_agent = judge_agent if judge_agent is not None else JudgeAgent()
        self.synthesis_agent = synthesis_agent if synthesis_agent is not None else SynthesisAgent()
        self.enable_checkpoints = enable_checkpoints
        self.checkpoint_manager = StateCheckpoint(checkpoint_dir) if enable_checkpoints else None
        self.graph = self._build_graph()
        logger.info(
            f"WorkflowOrchestrator initialized with max_iterations={max_iterations}, "
            f"checkpoints={'enabled' if enable_checkpoints else 'disabled'}"
        )
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state machine.
        
        Returns:
            Compiled StateGraph ready for execution
        """
        # Create the state graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes for each agent
        workflow.add_node("scout", self._scout_node)
        workflow.add_node("mapper", self._mapper_node)
        workflow.add_node("adversary", self._adversary_node)
        workflow.add_node("judge", self._judge_node)
        workflow.add_node("synthesis", self._synthesis_node)
        
        # Set entry point
        workflow.set_entry_point("scout")
        
        # Add edges for state transitions
        workflow.add_edge("scout", "mapper")
        workflow.add_edge("mapper", "adversary")
        
        # Add conditional edge for iteration logic
        workflow.add_conditional_edges(
            "adversary",
            self._should_continue_iteration,
            {
                "continue": "scout",  # Loop back for more evidence
                "proceed": "judge"    # Move to evaluation
            }
        )
        
        workflow.add_edge("judge", "synthesis")
        workflow.add_edge("synthesis", END)
        
        logger.debug("LangGraph state machine built successfully")
        return workflow.compile()
    
    def _save_checkpoint(self, state: WorkflowState, phase: str) -> None:
        """
        Save a checkpoint of the current state.
        
        Args:
            state: Current workflow state
            phase: Current phase name
        """
        if not self.enable_checkpoints or not self.checkpoint_manager:
            return
        
        try:
            checkpoint_id = f"{state.topic[:50].replace(' ', '_')}_{phase}_iter{state.iteration}"
            self.checkpoint_manager.save_checkpoint(state, checkpoint_id, format="json")
            logger.debug(f"Checkpoint saved: {checkpoint_id}")
        except Exception as e:
            logger.warning(f"Failed to save checkpoint for {phase}: {e}")
    
    def _scout_node(self, state: WorkflowState) -> WorkflowState:
        """
        Scout agent node: Gather diverse sources.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state with new sources
        """
        logger.info(f"Entering Scout phase (iteration {state.iteration})")
        log_agent_transition(logger, state.current_phase, "scout", state.iteration)
        state.current_phase = "scout"
        
        try:
            # Execute Scout agent
            state = self.scout_agent.execute(state)
            
            # Validate partial data - check if we have minimum sources
            is_valid, completeness = validate_partial_data(
                state,
                required_fields=['sources'],
                min_completeness=0.3  # Accept if we have at least 30% of expected data
            )
            
            if not is_valid:
                logger.warning(
                    f"Scout phase produced insufficient data (completeness: {completeness:.2%})"
                )
            
            # Save checkpoint after successful execution
            self._save_checkpoint(state, "scout")
            
        except Exception as e:
            logger.error(f"Scout phase failed: {e}")
            # Continue with partial data if available
            if not state.sources:
                state.status_message = f"Scout phase failed: {e}"
        
        return state
    
    def _mapper_node(self, state: WorkflowState) -> WorkflowState:
        """
        Mapper agent node: Extract entities, relationships, and conflicts.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state with knowledge graph
        """
        logger.info(f"Entering Mapper phase (iteration {state.iteration})")
        log_agent_transition(logger, state.current_phase, "mapper", state.iteration)
        state.current_phase = "mapper"
        
        try:
            # Execute Mapper agent
            state = self.mapper_agent.execute(state)
            
            # Validate partial data - check if we have knowledge graph
            if state.knowledge_graph:
                is_valid, completeness = validate_partial_data(
                    state.knowledge_graph,
                    required_fields=['entities', 'relationships'],
                    min_completeness=0.5
                )
                
                if not is_valid:
                    logger.warning(
                        f"Mapper phase produced incomplete knowledge graph "
                        f"(completeness: {completeness:.2%})"
                    )
            
            # Save checkpoint after successful execution
            self._save_checkpoint(state, "mapper")
            
        except Exception as e:
            logger.error(f"Mapper phase failed: {e}")
            state.status_message = f"Mapper phase failed: {e}"
        
        return state
    
    def _adversary_node(self, state: WorkflowState) -> WorkflowState:
        """
        Adversary agent node: Identify weaknesses and generate counter-queries.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state with adversarial queries
        """
        logger.info(f"Entering Adversary phase (iteration {state.iteration})")
        log_agent_transition(logger, state.current_phase, "adversary", state.iteration)
        state.current_phase = "adversary"
        
        try:
            # Execute Adversary agent
            state = self.adversary_agent.execute(state)
            
            # Save checkpoint after successful execution
            self._save_checkpoint(state, "adversary")
            
        except Exception as e:
            logger.error(f"Adversary phase failed: {e}")
            # Continue without adversarial queries
            state.adversarial_queries = []
            state.status_message = f"Adversary phase failed: {e}"
        
        # Increment iteration counter
        state.iteration += 1
        
        return state
    
    def _judge_node(self, state: WorkflowState) -> WorkflowState:
        """
        Judge agent node: Evaluate source credibility and weight claims.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state with credibility scores
        """
        logger.info("Entering Judge phase")
        log_agent_transition(logger, state.current_phase, "judge", state.iteration)
        state.current_phase = "judge"
        
        try:
            # Execute Judge agent
            state = self.judge_agent.execute(state)
            
            # Save checkpoint after successful execution
            self._save_checkpoint(state, "judge")
            
        except Exception as e:
            logger.error(f"Judge phase failed: {e}")
            state.status_message = f"Judge phase failed: {e}"
        
        return state
    
    def _synthesis_node(self, state: WorkflowState) -> WorkflowState:
        """
        Synthesis agent node: Generate final report with argument topology.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state with synthesis report
        """
        logger.info("Entering Synthesis phase")
        log_agent_transition(logger, state.current_phase, "synthesis", state.iteration)
        state.current_phase = "synthesis"
        
        try:
            # Execute Synthesis agent
            state = self.synthesis_agent.execute(state)
            
            # Save final checkpoint
            self._save_checkpoint(state, "synthesis")
            
        except Exception as e:
            logger.error(f"Synthesis phase failed: {e}")
            state.status_message = f"Synthesis phase failed: {e}"
        
        return state
    
    def _should_continue_iteration(self, state: WorkflowState) -> Literal["continue", "proceed"]:
        """
        Decision function to determine if another iteration is needed.
        
        Continues iteration if:
        - Weak claims are identified (adversarial queries generated)
        - Maximum iterations not yet reached
        
        Args:
            state: Current workflow state
            
        Returns:
            "continue" to loop back to Scout, "proceed" to move to Judge
        """
        # Check if max iterations reached
        if state.iteration >= state.max_iterations:
            logger.info(f"Maximum iterations ({state.max_iterations}) reached, proceeding to Judge")
            return "proceed"
        
        # Check if adversarial queries were generated (indicating weak claims)
        if state.adversarial_queries and len(state.adversarial_queries) > 0:
            logger.info(f"Weak claims found, continuing iteration {state.iteration + 1}")
            return "continue"
        
        # No weak claims found, proceed to evaluation
        logger.info("Sufficient evidence gathered, proceeding to Judge")
        return "proceed"
    
    def initialize(self, topic: str) -> WorkflowState:
        """
        Initialize the workflow with a research topic.
        
        Validates the topic and creates the initial workflow state.
        
        Args:
            topic: Research topic string
            
        Returns:
            Initialized WorkflowState
            
        Raises:
            ValueError: If topic is invalid (empty or whitespace-only)
        """
        logger.info(f"Initializing workflow with topic: '{topic}'")
        
        # Validate topic is non-empty and contains meaningful content
        if not topic or not topic.strip():
            logger.error("Topic validation failed: empty or whitespace-only")
            raise ValueError("Topic must be non-empty and contain meaningful content")
        
        # Check for meaningful content (not just special characters)
        if not any(c.isalnum() for c in topic):
            logger.error("Topic validation failed: no alphanumeric characters")
            raise ValueError("Topic must contain meaningful content (alphanumeric characters)")
        
        # Create initial workflow state
        state = WorkflowState(
            topic=topic.strip(),
            iteration=0,
            max_iterations=self.max_iterations,
            current_phase="initialized",
            status_message=f"Research workflow initialized for topic: '{topic.strip()}'"
        )
        
        logger.info(f"Workflow initialized successfully: {state.status_message}")
        return state
    
    def execute(self, topic: str) -> WorkflowState:
        """
        Execute the complete research workflow for a given topic.
        
        Args:
            topic: Research topic string
            
        Returns:
            Final WorkflowState with synthesis report
            
        Raises:
            ValueError: If topic is invalid
        """
        # Initialize workflow state
        state = self.initialize(topic)
        
        logger.info("Starting workflow execution")
        
        try:
            # Execute the graph
            final_state = self.graph.invoke(state)
            
            logger.info("Workflow execution completed successfully")
            return final_state
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            
            # Attempt to recover from last checkpoint
            if self.enable_checkpoints and self.checkpoint_manager:
                logger.info("Attempting to recover from last checkpoint")
                try:
                    checkpoints = self.checkpoint_manager.list_checkpoints()
                    # Filter checkpoints for this topic
                    topic_prefix = topic[:50].replace(' ', '_')
                    relevant_checkpoints = [
                        cp for cp in checkpoints if cp.startswith(topic_prefix)
                    ]
                    
                    if relevant_checkpoints:
                        # Load the most recent checkpoint
                        latest_checkpoint = sorted(relevant_checkpoints)[-1]
                        logger.info(f"Loading checkpoint: {latest_checkpoint}")
                        recovered_state = self.checkpoint_manager.load_checkpoint(
                            latest_checkpoint,
                            format="json",
                            state_class=WorkflowState
                        )
                        logger.info("State recovered from checkpoint")
                        return recovered_state
                    else:
                        logger.warning("No relevant checkpoints found for recovery")
                        
                except StateRecoveryError as recovery_error:
                    logger.error(f"State recovery failed: {recovery_error}")
            
            # Re-raise the original exception if recovery failed
            raise
    
    def recover_from_checkpoint(self, checkpoint_id: str) -> WorkflowState:
        """
        Recover workflow state from a specific checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint to recover from
            
        Returns:
            Recovered WorkflowState
            
        Raises:
            StateRecoveryError: If recovery fails
        """
        if not self.enable_checkpoints or not self.checkpoint_manager:
            raise StateRecoveryError("Checkpointing is not enabled")
        
        logger.info(f"Recovering from checkpoint: {checkpoint_id}")
        
        state = self.checkpoint_manager.load_checkpoint(
            checkpoint_id,
            format="json",
            state_class=WorkflowState
        )
        
        logger.info("State recovered successfully")
        return state

