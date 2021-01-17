import httpx

from fastapi.responses import PlainTextResponse
from fastapi import Path, Query, APIRouter


router = APIRouter()

@router.get("/_teapot", status_code=418, response_class=PlainTextResponse)
async def get_teapot():
    return '''418. I’m a teapot :(
You are attempting to brew coffee with a teapot, but I'm just a teapot :(

ref: https://tools.ietf.org/html/rfc2324#section-2.3.2

             ;,'
     _o_    ;:;'
 ,-.'---`.__ ;
((j`=====',-'
 `-\     /
    `-=-'
'''