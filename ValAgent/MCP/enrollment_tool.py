from server import mcp
from server import http_get, http_post
from config import ENROLLMENT_URL
from models import EnrollmentCreateIn,EnrollmentCreateOut, EnrollmentOut
from typing import Optional, Annotated

@mcp.tool(
    name="enroll_course",
    description="Create an enrollment after payment has been completed. Payment must be done for the enrollment."
)
async def enroll_course(
    enroll_input: EnrollmentCreateIn
) -> EnrollmentCreateOut:
    """
    Calls POST /enrollment with:
    {
        "user_id": int,
        "course_id": int,
        "payment_id": int
    }
    """

    url = f"{ENROLLMENT_URL.rstrip('/')}/enrollment"

    resp = await http_post(
        url,
        headers={
            "accept": "application/json",
            "Content-Type": "application/json",
        },
        body=enroll_input.model_dump(),
    )

    return EnrollmentCreateOut(**resp)


@mcp.tool(
    name="get_enrollment_by_id",
    description="Fetch an enrollment record by enrollment_id."
)
async def get_enrollment_by_id(
    enrollment_id: Annotated[int, "The enrollment ID to fetch"]
) -> EnrollmentOut:
    """
    Calls GET /enrollment/{id}
    """

    url = f"{ENROLLMENT_URL.rstrip('/')}/{enrollment_id}"

    resp = await http_get(
        url,
        headers={
            "accept": "application/json",
        }
    )

    return EnrollmentOut(**resp)
