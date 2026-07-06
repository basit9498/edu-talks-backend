from langchain_core.tools import tool
from app.services.google import tool_save_google_drive
from app.schemas.ai_planner import ToolUserGoogleCredentials


@tool
async def agent_tool_google_doc(user: ToolUserGoogleCredentials, roadmap: str):
    """Upload the roadmap to Google Drive Cloud Storage.
    taking user info that will google_access_token and google_refresh_token
    so you much take user as well

    """
    await tool_save_google_drive(user, roadmap)
    return "SUCCESS: Roadmap uploaded to Google Drive Doc."
