# tests/test_agent.py
import pytest
import pytest_asyncio
from langgraph.types import Command
from agent_core import init_agent_system

@pytest_asyncio.fixture
async def agent_executor():
    """Fixture pour initialiser l'agent une seule fois pour les tests."""
    return await init_agent_system()

@pytest.fixture
def test_config():
    """Configuration de session unique pour isoler le thread de test."""
    return {"configurable": {"thread_id": "pytest_session_thread"}}

@pytest.mark.asyncio
async def test_hitl_trigger_and_rejection(agent_executor, test_config):
    """Vérifie que l'agent s'interrompt sur un prompt critique et réagit correctement au rejet."""
    critical_prompt = "Envoie un e-mail à boss@company.com pour lui dire que je démissionne."
    
    # 1. Envoi du prompt critique : l'agent doit s'arrêter
    response = await agent_executor.ainvoke(
        {"messages": [("user", critical_prompt)]}, 
        config=test_config
    )
    
    # Vérification de l'état du graphe (doit être en pause)
    current_state = await agent_executor.aget_state(test_config)
    assert len(current_state.next) > 0, "L'agent aurait dû s'interrompre avant l'exécution de l'outil."
    assert "HumanInTheLoopMiddleware" in current_state.next[0]

    # 2. Simulation d'un REJET humain (Annulation)
    num_tool_calls = len(getattr(response["messages"][-1], "tool_calls", [1]))
    decisions = [{"type": "reject", "message": "Refusé par le test unitaire."} for _ in range(num_tool_calls)]
    
    final_response = await agent_executor.ainvoke(
        Command(resume={"decisions": decisions}),
        config=test_config
    )
    
    # L'état final ne doit plus être en pause
    post_state = await agent_executor.aget_state(test_config)
    assert not post_state.next, "Le graphe est toujours bloqué après la commande resume."
    
    # L'agent doit confirmer qu'il n'a pas fait l'action
    last_message_content = final_response["messages"][-1].content.lower()
    assert any(x in last_message_content for x in ["pas", "refus", "confirmation", "annul"]), \
        "L'agent n'a pas semblé prendre en compte le refus dans sa réponse finale."

@pytest.mark.asyncio
async def test_hitl_approval(agent_executor):
    """Vérifie que l'agent poursuit son exécution après une approbation humaine."""
    # On utilise un thread différent pour ne pas polluer le test précédent
    specific_config = {"configurable": {"thread_id": "pytest_approval_thread"}}
    critical_prompt = "Envoie un e-mail à boss@company.com pour lui dire que je démissionne."
    
    # Envoi initial
    response = await agent_executor.ainvoke(
        {"messages": [("user", critical_prompt)]}, 
        config=specific_config
    )
    
    # Simulation d'une APPROBATION humaine
    num_tool_calls = len(getattr(response["messages"][-1], "tool_calls", [1]))
    decisions = [{"type": "approve"} for _ in range(num_tool_calls)]
    
    final_response = await agent_executor.ainvoke(
        Command(resume={"decisions": decisions}),
        config=specific_config
    )
    
    # Vérification que le graphe a fini sa course
    post_state = await agent_executor.aget_state(specific_config)
    assert not post_state.next
    assert len(final_response["messages"]) > 0