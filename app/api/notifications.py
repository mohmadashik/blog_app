import asyncio
import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.deps import require_role
from app.model.user import Role
from app.services.notifications import notifier

router = APIRouter()


@router.get("/sse")
async def notifications_sse(
    request: Request,
    current_admin = Depends(require_role(Role.admin, Role.approver)),
):
    """
    SSE stream for admins/approvers.
    Emits an event whenever a new pending blog is created.
    """

    async def event_generator():
        queue = await notifier.connect()
        try:
            while True:
                # stop if client disconnected
                if await request.is_disconnected():
                    break

                try:
                    # wait for next event with timeout just to send keep-alive
                    event = await asyncio.wait_for(queue.get(), timeout=15.0)
                    data_str = json.dumps(event)
                    yield f"data: {data_str}\n\n"
                except asyncio.TimeoutError:
                    # keep connection alive
                    yield ": keep-alive\n\n"
        finally:
            notifier.disconnect(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
