import asyncio
import logging

from fastmcp import FastMCP
from starlette.responses import JSONResponse

from usa_spending_mcp_server.client import USASpendingClient
from usa_spending_mcp_server.tools.agency_spending import register_agency_tools
from usa_spending_mcp_server.tools.award_spending import register_award_search_tools

logger = logging.getLogger(__name__)

# Create FastMCP instance with detailed instructions
mcp = FastMCP(
    name="USASpendingServer",
    instructions="""
    This server provides comprehensive access to USA government spending data through the
    USAspending.gov API. Use this server when you are interested in data from multiple agencies
    or from agencies other than the National Institutes of Health (NIH)

    ## Quick Tool Selection Guide:

    **"Show me the largest grants awarded by [agency]"**
    → Use search_spending_by_award() with agencies filter and award_type_codes=["02","03","04","05"]

    **"What are the details of grant XYZ?"**
    → Use search_spending_by_award() with award_ids filter

    ## Tool Categories & When to Use:

    ### 🔍 REFERENCE TOOLS (Always Start Here)
    **Use when:** You need agency codes, award types, or term definitions
    - get_agencies(): Get list of all US agencies with their codes and IDs
    - get_award_types(): Get available award type codes (A=BPA, B=IDV, C=Contract, D=Grant, etc.)
    - get_glossary(): Get definitions of spending terms

    ### 📝 INDIVIDUAL AWARDS/CONTRACTS
    **Use when:** You need specific grant details or want to search individual grant awards
    - search_spending_by_award(): **BEST FOR:**
      * "Show me all grants awarded to the University of Michigan"
      * "Find all biotechnology grants over $10 million"
      * "What grants did NIH award in 2023 related to health disparities?"
      * "Details of specific award ID"
    **Returns:** Individual award records with full details

    ## Decision Matrix:

    | Question Type | Primary Tool | Secondary Tools |
    |---------------|-------------|-----------------|
    | Agency spending totals/rankings | search_spending_explorer | get_agencies |
    | Agency organizational structure | get_sub_components_list | list_program_activities |
    | Individual grant details | search_spending_by_award | get_award_details |

    ## Common Mistakes to Avoid:

    ❌ **Don't forget to get agency codes first**
    ✅ **Start with get_agencies() to find correct agency names/codes**

    ## Key Parameters:

    ### Time Periods:
    - **FY 2024:** 2023-10-01 to 2024-09-30 (default)
    - **FY 2023:** 2022-10-01 to 2023-09-30
    - Format: YYYY-MM-DD

    ### Award Types:
    Grants:
      - **02:** Block Grant 
      - **03:** Formula Grant
      - **04:** Project Grant 
      - **05:** Cooperative Agreement 
    - **Use get_award_types() for complete list**
    
    ### Geographic Codes:
    - **States:** Use 2-letter postal codes (CA, TX, NY)
    - **Counties:** Use 5-digit FIPS codes (06037 for Los Angeles County)
    - **Districts:** Use state + district (CA12, TX01)
    - **ZIP:** Use 5-digit ZIP codes (90210, 20500)

    ## Best Practices:

    1. **Always start with reference tools** to get proper agency names and codes
    2. **Match tool to question type** using the decision matrix above
    3. **Use appropriate pagination** (default 100, increase for comprehensive results)
    4. **Verify agency names** - use exact names from get_agencies()
    5. **For geographic analysis,** choose place_of_performance vs recipient_location carefully

    ## Performance Tips:
    - Limit award details requests to 10 awards per call
    - Use fetch_all_pages=True cautiously with max_pages limits
    - Start with smaller date ranges for large queries

    Always provide clear, actionable insights based on the spending data retrieved.
    """,
)

# health check 
@mcp.custom_route("/health", method=['GET'])
async def health_check(request):
    return JSONResponse({"status": "healthy", "service": "mcp-server"})


def main():
    """Main entry point"""
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting USA Spending MCP Server")

    # Run the asynchronous main function
    asyncio.run(async_main())


async def async_main():
    """Async entry point"""
    # Initialize HTTP client
    async with USASpendingClient() as client:
        # Register tools
        logger.info("Registering tools")
        register_agency_tools(mcp, client)
        register_award_search_tools(mcp, client)
        logger.info("Running USA Spending MCP Server")
        await mcp.run_async()

app = mcp.http_app(stateless_http=True)

# if __name__ == "__main__":
#     main()
