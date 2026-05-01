from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    code: int = 200
    msg: str = "success"
    data: Optional[T] = None

# 成功快速返回
def success(data: any = None, msg: str = "success") -> ApiResponse:
    return ApiResponse(code=200, msg=msg, data=data)