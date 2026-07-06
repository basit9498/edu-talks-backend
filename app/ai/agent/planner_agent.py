from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_core.messages import BaseMessage, HumanMessage
from app.ai.agent.ai_brain import LLM, GrokModel
from app.ai.core.prompt_template import LLMPromptTemplate
from app.ai.agent.agent_tool import agent_tool_google_doc
from app.config import settings

from typing import TypedDict, Annotated, List, Any
import json


class PlannerAgentState(TypedDict, total=False):
    user_query: str
    user_current_level: str
    demand_duration: float
    primary_goal: str
    roadmap: str
    approved_roadmap: bool
    feedback: str
    save_status: bool
    refine_status: bool
    user: Any
    messages: Annotated[list[BaseMessage], add_messages]


class PlannerAgent:
    def __init__(self, llm: LLM):
        self._llm = llm
        self._template = LLMPromptTemplate()

    def make_roadmap(
        self,
        user_query: str,
        current_level: str,
        demand_duration: str,
        primary_goal: str,
    ):
        # prompt need
        template = self._template.make_roadmap_template()
        prompt = template.invoke(
            {
                "user_query": user_query,
                "current_level": current_level,
                "demand_duration": demand_duration,
                "primary_goal": primary_goal,
            }
        )
        response = self._llm.invoke(prompt)
        return json.loads(response.content)

    def refine_roadmap(self, user_feedback, current_roadmap):
        # prompt need
        template = self._template.refine_roadmap_template()
        prompt = template.invoke(
            {
                "user_feedback": user_feedback,
                "current_roadmap": current_roadmap,
            }
        )
        print("LLM Called", prompt)
        response = self._llm.invoke(prompt)
        return json.loads(response.content)

    def get_save_template(self, roadmap: str, user):
        template = self._template.save_roadmap_template()
        return template.invoke({"road_map": roadmap, "user": user})

    def get_save_simple_template(self, roadmap: str, user):
        return self._template.save_roadmap_template_simple(road_map=roadmap, user=user)

    def save_roadmap(self, messages):
        tools_list = [agent_tool_google_doc]
        llm_with_tool = self._llm.llm_with_tool(prompt=messages, tools=tools_list)
        return llm_with_tool


class PlannerAgenticWorkflow:

    def __init__(self, agent: PlannerAgent, checkpointer: AsyncPostgresSaver):
        # agent
        self._agent = agent

        # graph state
        self._graph = StateGraph(PlannerAgentState)

        # checkpointer
        # self._checkpointer = InMemorySaver()
        self._checkpointer = checkpointer

        # graph init
        self._build_graph()

        # graph compile
        self._workflow = self._graph.compile(checkpointer=self._checkpointer)

    def _build_graph(self):
        # tool node
        tool_node = ToolNode([agent_tool_google_doc])
        # node
        self._graph.add_node("make_roadmap", self._make_roadmap)
        self._graph.add_node("user_approval", self._user_approval)
        self._graph.add_node("save_roadmap", self._save_roadmap)
        self._graph.add_node("refine_roadmap", self._refine_roadmap)
        self._graph.add_node("tools", tool_node)
        # edge connection

        self._graph.add_edge(START, "make_roadmap")
        self._graph.add_edge("make_roadmap", "user_approval")

        self._graph.add_conditional_edges(
            "user_approval",
            self._approved_route,
            {"next": "save_roadmap", "refine": "refine_roadmap"},
        )

        self._graph.add_edge("refine_roadmap", "user_approval")

        self._graph.add_conditional_edges("save_roadmap", tools_condition)
        self._graph.add_edge("tools", "save_roadmap")

    # graph methods detail
    async def _make_roadmap(self, state: PlannerAgentState):
        result = self._agent.make_roadmap(
            user_query=state["user_query"],
            current_level=state["user_current_level"],
            demand_duration=state["demand_duration"],
            primary_goal=state["primary_goal"],
        )

        # result = {"roadmap": {"roadmap": {"message": "testing LLM Response"}}}
        return {
            "roadmap": result,
        }

    async def _user_approval(self, state: PlannerAgentState):
        user_decision = interrupt(
            {
                "type": "approval_status",
                "reason": "User approval need for next step",
                "question": "Are you want to refine or approve the roadmap",
                "instruction": "Approve this roadmap or refine?",
            }
        )
        if (
            user_decision["approval_status"] == "Yes"
            or user_decision["approval_status"] == "yes"
            or user_decision["approval_status"] == "y"
        ):

            message_template = self._agent.get_save_simple_template(
                state["roadmap"], state["user"]
            )
            print("message_template", message_template)

            return {
                "approved_roadmap": True,
                "feedback": None,
                "messages": message_template,
            }
        else:
            return {
                "approved_roadmap": False,
                "feedback": user_decision["approval_status"],
            }

    async def _approved_route(self, state: PlannerAgentState):

        if state["approved_roadmap"]:
            return "next"
        else:
            return "refine"

    async def _save_roadmap(self, state: PlannerAgentState):

        messages = state.get("messages", [])
        if not messages:
            raise ValueError("No messages found in state. Cannot save roadmap.")

        response = self._agent.save_roadmap(messages=messages)
        return {"save_status": True, "messages": [response]}

    async def _refine_roadmap(self, state: PlannerAgentState):
        # print("__refine__Called", state["feedback"])
        result = self._agent.refine_roadmap(
            user_feedback=state["feedback"],
            current_roadmap=state["roadmap"]["roadmap"],
        )
        print("__refine__Called", result)
        return {"roadmap": result}

    # calling the graph section
    def run(self, state: PlannerAgentState, config):
        return self._workflow.invoke(state, config=config)

    async def run_async(self, state: PlannerAgentState, config):
        return await self._workflow.ainvoke(state, config=config)

    async def resume_async(self, resume_state, config):
        return await self._workflow.ainvoke(Command(resume=resume_state), config=config)

    async def run_stream(self, state: PlannerAgentState, config):
        """Stream the workflow execution to handle interrupts"""
        async for event in self._workflow.astream(state, config=config):
            yield event


# grok_model = GrokModel()
# planner_agent = PlannerAgent(llm=grok_model)
# planner_agentic_workflow = PlannerAgenticWorkflow(planner_agent)
