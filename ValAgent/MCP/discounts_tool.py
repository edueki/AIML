from server import mcp
from server import http_get, http_post
from config import DISCOUNT_URL
from models import DiscountApplyOut,ListDiscountsOut, DiscountOut, DiscountApplyIn

@mcp.tool(
    name="list_discounts",
    description="Retrieve the list of available discount codes for all courses."
)
async def list_discounts() -> ListDiscountsOut:
    """
    Calls GET /discount to fetch course discount records.
    """
    url = f"{DISCOUNT_URL.rstrip('/')}/discount"

    resp = await http_get(
        url,
        headers={"accept": "application/json"}
    )

    return ListDiscountsOut(
        items=[DiscountOut(**item) for item in resp.get("data", [])]
    )

@mcp.tool(
    name="apply_discount",
    description="Apply a discount code to a course and return discounted price details."
)
async def apply_discount(discount_input: DiscountApplyIn) -> DiscountApplyOut:
    """
    Calls POST /discount/apply with:
    {
        'course_id': int,
        'code': str
    }
    Returns discounted price breakdown.
    """

    url = f"{DISCOUNT_URL.rstrip('/')}/discount/apply"

    resp = await http_post(
        url,
        headers={
            "accept": "application/json",
            "Content-Type": "application/json",
        },
        body=discount_input.model_dump()
    )

    return DiscountApplyOut(**resp)
