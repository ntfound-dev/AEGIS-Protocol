import os
import json
import asyncio
from typing import Any, Dict

from uagents import Agent, Context, Model, Protocol  # type: ignore
from uagents.setup import fund_agent_if_low  # type: ignore

# --- DATA MODEL (harus sama dengan validator_agent.py) ---
class ValidatedEvent(Model):
    event_type: str
    severity: str
    details_json: str
    confidence_score: float

class ActionResponse(Model):
    status: str
    message: str


# --- CONFIGURATION ---
ACTION_AGENT_SEED = os.getenv("ACTION_AGENT_SEED", "action_agent_secret_seed_phrase_placeholder")

# --- AGENT INITIALIZATION ---
action_agent = Agent(
    name="action_agent_alpha",
    port=8003,
    seed=ACTION_AGENT_SEED,
    endpoint=["http://action-agent-1:8003/submit"],  # sesuaikan dengan docker-compose
)
fund_agent_if_low(str(action_agent.wallet.address()))
action_agent._logger.info(f"Action Agent running with address: {action_agent.address}")


# --- PROTOCOL ---
action_protocol = Protocol("ActionAPI")


# --- CORE LOGIC ---
async def persist_event_to_chain(ctx: Context, event: ValidatedEvent) -> bool:
    """
    Simpan event ke Event Factory canister (Internet Computer).
    Panggil declare_event.
    """
    try:
        # ambil EVENT_FACTORY_CANISTER_ID dari env
        canister_id = os.getenv("EVENT_FACTORY_CANISTER_ID")
        if not canister_id:
            ctx.logger.error("ENV EVENT_FACTORY_CANISTER_ID tidak diatur.")
            return False

        # construct payload untuk declare_event
        event_payload: Dict[str, Any] = {
            "event_type": event.event_type,
            "severity": event.severity,
            "details_json": event.details_json,
        }

        # gunakan dfx canister call (sementara, bisa diganti ic-py)
        import subprocess
        cmd = [
            "dfx", "canister", "call", canister_id,
            "declare_event",
            f'(record {{ event_type="{event_payload["event_type"]}"; severity="{event_payload["severity"]}"; details_json="{event_payload["details_json"]}" }})'
        ]
        ctx.logger.info(f"Menjalankan perintah: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            ctx.logger.error(f"Gagal menyimpan event ke chain: {result.stderr}")
            return False

        ctx.logger.info(f"Event berhasil disimpan ke chain: {result.stdout}")
        return True

    except Exception as e:
        ctx.logger.error(f"Exception saat simpan ke chain: {e}")
        return False


# --- EVENT HANDLER ---
@action_agent.on_message(model=ValidatedEvent)  # type: ignore
async def handle_validated_event(ctx: Context, sender: str, msg: ValidatedEvent):
    ctx.logger.info(f"Menerima ValidatedEvent dari {sender}: {msg.event_type} - {msg.severity}")

    # Simpan ke on-chain
    success = await persist_event_to_chain(ctx, msg)

    if success:
        ctx.logger.info("Validated event berhasil diproses dan disimpan.")
    else:
        ctx.logger.warning("Validated event diterima, tapi gagal disimpan ke chain.")


@action_protocol.on_query(model=ValidatedEvent, replies=ActionResponse)  # type: ignore
async def handle_query_event(ctx: Context, sender: str, msg: ValidatedEvent):
    ctx.logger.info(f"Query ValidatedEvent diterima dari {sender}")
    success = await persist_event_to_chain(ctx, msg)

    if success:
        await ctx.send(sender, ActionResponse(status="success", message="Event stored on-chain."))
    else:
        await ctx.send(sender, ActionResponse(status="error", message="Failed to store event."))


# --- MAIN ---
action_agent.include(action_protocol)

if __name__ == "__main__":
    action_agent.run()
