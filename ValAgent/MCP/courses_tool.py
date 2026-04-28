from server import mcp
from server import http_get
from config import  COURSES_URL
from typing import Dict, Any

@mcp.tool(
    name="list_courses",
    description="Returns list of available courses for the enrollment.")
async def list_courses() -> Dict[str, Any]:
    """
    Lists all courses with pagination
    Returns a paginated list of available courses.
    """
    url = f"{COURSES_URL.rstrip('/')}/courses"
    return await http_get(url, headers={"accept": "application/json"})

@mcp.tool(
    name="get_course_by_id",
    description="Get single course details by its course ID")
async def list_course_id(course_id: int) -> Dict[str, Any]:
    """
    Calls GET /courses/{id} to fetch details of a single course
    """
    url = f"{COURSES_URL.rstrip('/')}/courses/{course_id}"
    return await http_get(url, headers={"accept": "application/json"})