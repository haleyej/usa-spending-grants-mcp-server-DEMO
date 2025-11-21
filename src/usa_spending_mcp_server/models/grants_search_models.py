from typing import Annotated 
from pydantic import Field, field_validator

from usa_spending_mcp_server.models.common_models import (
    BaseSearchRequest
)


class GrantSearchRequest(BaseSearchRequest):
    pass 