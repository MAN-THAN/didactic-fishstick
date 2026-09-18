from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import ai_service
from app.dependencies.auth_dependency import get_current_user
from app.models.user_model import User
from fastapi.responses import StreamingResponse
from app.services import ai_service 
from fastapi.sse import EventSourceResponse, ServerSentEvent
from app.ai.agents.task_agent import create_task_agent
import json
from collections.abc import AsyncGenerator
from pydantic import BaseModel, Field
from app.schemas.ai_schema import AIChatRequest
from langchain_core.messages import AIMessageChunk



router = APIRouter(prefix='/ai', tags=['AI'],dependencies=[Depends(get_current_user)])

@router.get('/dashboard_summary', response_class=EventSourceResponse)
async def get_dashboard_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get a summary of the user's dashboard, including task priorities, overdue tasks, and recommendations.
    """
    async for event in ai_service.stream_dashboard_summary(
        current_user,
        db,
    ):
        yield ServerSentEvent(
            event=event["event"],
            data=event["data"],
        )




# =========================================================
# SSE HELPER
# =========================================================


def create_sse_event(
    event_type: str,
    data: dict,
) -> str:
    """
    Convert event type + dictionary into a valid SSE message.
    """

    return (
        f"event: {event_type}\n"
        f"data: {json.dumps(data, ensure_ascii=False, default=str)}\n\n"
    )


# =========================================================
# AGENT STREAM
# =========================================================


async def stream_agent_response(
    message: str,
    current_user,
    db: Session,
) -> AsyncGenerator[str, None]:
    """
    Run the LangChain agent and convert LangChain stream
    events into frontend-friendly SSE events.
    """

    try:
        # =================================================
        # START
        # =================================================

        yield create_sse_event(
            "start",
            {
                "message": "AI assistant started.",
            },
        )

        # =================================================
        # CREATE AGENT
        # =================================================

        agent = create_task_agent(
            current_user=current_user,
            db=db,
        )

        yield create_sse_event(
            "agent_started",
            {
                "agent": "task_agent",
                "message": "Task agent is processing your request.",
            },
        )

        # =================================================
        # START LANGCHAIN STREAM
        # =================================================

        async for chunk in agent.astream(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": message,
                    }
                ]
            },
            stream_mode=[
                "messages",
                "updates",
                "custom",
            ],
            version="v2",
        ):

            # =================================================
            # MESSAGE STREAM
            #
            # Contains LLM token chunks.
            # =================================================

            if chunk["type"] == "messages":

                message_chunk, metadata = chunk["data"]
                if not isinstance(message_chunk, AIMessageChunk):
                    continue

                 # Extra protection: only model node output
                if metadata.get("langgraph_node") != "model":
                     continue

                # -------------------------------------------------
                # NORMAL TEXT TOKEN
                # -------------------------------------------------

                token_text = getattr(
                    message_chunk,
                    "text",
                    None,
                )

                if token_text:
                    yield create_sse_event(
                        "token",
                        {
                            "content": token_text,
                            "node": metadata.get(
                                "langgraph_node"
                            ),
                        },
                    )

                # -------------------------------------------------
                # TOOL CALL DELTA
                #
                # This contains partial tool call information
                # while the model is generating the tool call.
                # -------------------------------------------------

                tool_call_chunks = getattr(
                    message_chunk,
                    "tool_call_chunks",
                    None,
                )

                if tool_call_chunks:

                    for tool_call in tool_call_chunks:

                        yield create_sse_event(
                            "tool_call_delta",
                            {
                                "name": tool_call.get("name"),
                                "args": tool_call.get("args"),
                                "id": tool_call.get("id"),
                                "index": tool_call.get("index"),
                            },
                        )

            # =================================================
            # AGENT STEP UPDATES
            #
            # Useful for detecting:
            # model -> tool call
            # tool -> result
            # =================================================

            elif chunk["type"] == "updates":

                updates = chunk["data"]

                for source, update in updates.items():

                    if not isinstance(update, dict):
                        continue

                    messages = update.get(
                        "messages",
                        [],
                    )

                    if not messages:
                        continue

                    last_message = messages[-1]

                    # =================================================
                    # MODEL UPDATE
                    # =================================================

                    if source == "model":

                        tool_calls = getattr(
                            last_message,
                            "tool_calls",
                            [],
                        )

                        if tool_calls:

                            for tool_call in tool_calls:

                                yield create_sse_event(
                                    "tool_call",
                                    {
                                        "name": tool_call.get(
                                            "name"
                                        ),
                                        "args": tool_call.get(
                                            "args"
                                        ),
                                        "id": tool_call.get(
                                            "id"
                                        ),
                                    },
                                )

                    # =================================================
                    # TOOL UPDATE
                    # =================================================

                    elif source == "tools":

                        tool_name = getattr(
                            last_message,
                            "name",
                            None,
                        )

                        tool_call_id = getattr(
                            last_message,
                            "tool_call_id",
                            None,
                        )

                        content = getattr(
                            last_message,
                            "content",
                            None,
                        )

                        yield create_sse_event(
                            "tool_result",
                            {
                                "name": tool_name,
                                "tool_call_id": tool_call_id,
                                "content": content,
                            },
                        )

            # =================================================
            # CUSTOM EVENTS
            #
            # These come from get_stream_writer()
            # inside your tools.
            # =================================================

            elif chunk["type"] == "custom":

                custom_data = chunk["data"]

                if isinstance(custom_data, dict):

                    yield create_sse_event(
                        "tool_activity",
                        custom_data,
                    )

                else:

                    yield create_sse_event(
                        "tool_activity",
                        {
                            "message": str(
                                custom_data
                            ),
                        },
                    )

        # =================================================
        # COMPLETED
        # =================================================

        yield create_sse_event(
            "done",
            {
                "message": "AI assistant finished.",
            },
        )

    except Exception as exc:

        # =================================================
        # ERROR
        # =================================================

        yield create_sse_event(
            "error",
            {
                "message": str(exc),
            },
        )


# =========================================================
# AI CHAT ENDPOINT
# =========================================================


@router.post("/task_assistant")
async def ai_chat(
    request: AIChatRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Stream AI task assistant response using Server-Sent Events.
    """

    return StreamingResponse(
        stream_agent_response(
            message=request.message,
            current_user=current_user,
            db=db,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
      


