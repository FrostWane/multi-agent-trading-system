from app.agents.workflow import AGENT_SEQUENCE, run_analysis_workflow


def test_workflow_runs_all_specialist_agents():
    events = []

    def emit(agent, status, message, payload=None):
        events.append((agent, status, message, payload))

    result = run_analysis_workflow(
        {
            "symbol": "000001",
            "start_date": "2024-01-01",
            "end_date": "2024-06-30",
            "horizon": "1m",
            "risk_preference": "balanced",
        },
        emit=emit,
    )

    completed_agents = {agent for agent, status, *_ in events if status == "completed"}
    assert set(AGENT_SEQUENCE) <= completed_agents
    assert result["report"]["summary"]
    assert result["report"]["llm_enabled"] is False
    assert result["critic"]["passed"] is True
