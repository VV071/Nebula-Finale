from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.workers.live_monitor import live_monitor
import logging

router = APIRouter(prefix="/api/live", tags=["Live News"])

logger = logging.getLogger(__name__)


@router.websocket("/stream")
async def live_news_stream(websocket: WebSocket):
    """
    WebSocket endpoint for live news streaming.
    
    Connect to receive real-time updates when new articles are analyzed.
    
    Messages sent:
    - {"type": "new_article", "article": {...}}
    - {"type": "stats_update", "stats": {...}}
    - {"type": "connected", "message": "..."}
    """
    await websocket.accept()
    
    # Add to subscribers
    live_monitor.add_subscriber(websocket)
    
    # Send welcome message
    await websocket.send_json({
        "type": "connected",
        "message": "Connected to live news stream",
        "interval_minutes": live_monitor.interval_minutes,
        "total_processed": live_monitor.total_processed
    })
    
    try:
        # Keep connection alive and handle client messages
        while True:
            # Wait for client ping/pong
            data = await websocket.receive_text()
            
            # Handle client requests
            if data == "stats":
                await websocket.send_json({
                    "type": "stats",
                    "total_processed": live_monitor.total_processed,
                    "last_fetch": live_monitor.last_fetch_time.isoformat() if live_monitor.last_fetch_time else None,
                    "subscribers": len(live_monitor.live_subscribers)
                })
                
    except WebSocketDisconnect:
        live_monitor.remove_subscriber(websocket)
        logger.info("Client disconnected from live stream")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        live_monitor.remove_subscriber(websocket)


@router.get("/status")
async def get_live_status():
    """Get the status of the live news monitor."""
    return {
        "status": "running" if live_monitor.scheduler.running else "stopped",
        "interval_minutes": live_monitor.interval_minutes,
        "total_processed": live_monitor.total_processed,
        "last_fetch": live_monitor.last_fetch_time.isoformat() if live_monitor.last_fetch_time else None,
        "active_subscribers": len(live_monitor.live_subscribers)
    }


@router.post("/trigger")
async def trigger_immediate_fetch():
    """Manually trigger an immediate news fetch."""
    await live_monitor.fetch_latest_news()
    return {
        "status": "triggered",
        "message": "Immediate fetch started"
    }
