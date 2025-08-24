from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
    StartSessionContent,
    EndSessionContent,
)
from functions import get_earthquakes, EarthquakeRequest, EarthquakeResponse
from datetime import datetime
from uuid import uuid4
from typing import Any, Dict
from uagents import Model

class StructuredOutputPrompt(Model):
    prompt: str
    output_schema: Dict[str, Any]

class StructuredOutputResponse(Model):
    output: Dict[str, Any]

# Replace this with your AI agent address
AI_AGENT_ADDRESS = "agent1qtlpfshtlcxekgrfcpmv7m9zpajuwu7d5jfyachvpa4u3dkt6k0uwwp2lct"

agent = Agent()

chat_proto = Protocol(spec=chat_protocol_spec)
struct_output_client_proto = Protocol(
    name="StructuredOutputClientProtocol", version="0.1.0"
)

def create_text_chat(text: str, end_session: bool = False) -> ChatMessage:
    content = [TextContent(type="text", text=text)]
    if end_session:
        content.append(EndSessionContent(type="end-session"))
    return ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=content,
    )

@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle incoming chat messages and request structured output from the AI agent.

    The AI agent is expected to return a structured object matching EarthquakeRequest.schema(),
    containing at least `location` and optional `radius_km` and `days`.
    """
    ctx.logger.info(f"Got a message from {sender}: {msg.content}")
    ctx.storage.set(str(ctx.session), sender)
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.utcnow(), acknowledged_msg_id=msg.msg_id),
    )

    for item in msg.content:
        if isinstance(item, StartSessionContent):
            ctx.logger.info(f"Got a start session message from {sender}")
            continue
        elif isinstance(item, TextContent):
            ctx.logger.info(f"Got a message from {sender}: {item.text}")
            ctx.storage.set(str(ctx.session), sender)
            # Ask the AI agent to produce structured output according to EarthquakeRequest
            await ctx.send(
                AI_AGENT_ADDRESS,
                StructuredOutputPrompt(
                    prompt=item.text,
                    output_schema=EarthquakeRequest.schema()
                ),
            )
        else:
            ctx.logger.info(f"Got unexpected content from {sender}")

@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(
        f"Got an acknowledgement from {sender} for {msg.acknowledged_msg_id}"
    )

@struct_output_client_proto.on_message(StructuredOutputResponse)
async def handle_structured_output_response(
    ctx: Context, sender: str, msg: StructuredOutputResponse
):
    """Receive structured output from the AI agent, call get_earthquakes(), and reply to the session sender."""
    ctx.logger.info(f'Here is the message from structured output {msg.output}')
    session_sender = ctx.storage.get(str(ctx.session))
    if session_sender is None:
        ctx.logger.error(
            "Discarding message because no session sender found in storage"
        )
        return

    # Basic unknown check
    if "<UNKNOWN>" in str(msg.output):
        await ctx.send(
            session_sender,
            create_text_chat(
                "Sorry, I couldn't process your location request. Please try again later."
            ),
        )
        return

    # Extract fields safely
    try:
        output = msg.output if isinstance(msg.output, dict) else {}
        location = output.get("location")
        radius_km = output.get("radius_km") or output.get("radius") or 200
        days = output.get("days") or 7
    except Exception:
        location = None
        radius_km = 200
        days = 7

    try:
        if not location:
            raise ValueError("No location provided in structured output")
        # Call the earthquake helper and build a reply
        result = get_earthquakes(location, int(radius_km), int(days))
        ctx.logger.info(str(result))
    except Exception as err:
        ctx.logger.error(f"Error: {err}")
        await ctx.send(
            session_sender,
            create_text_chat(
                "Sorry, I couldn't process your request. Please try again later."
            ),
        )
        return

    if "error" in result:
        await ctx.send(session_sender, create_text_chat(str(result["error"])) )
        return

    reply = result.get("earthquakes") or f"No earthquake data for {location}."
    chat_message = create_text_chat(reply)

    await ctx.send(session_sender, chat_message)

# Include protocols and run the agent
agent.include(chat_proto, publish_manifest=True)
agent.include(struct_output_client_proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
