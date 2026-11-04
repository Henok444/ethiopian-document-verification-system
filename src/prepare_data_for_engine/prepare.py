import json
from fastapi import HTTPException



async def load_request(json_file):


    try:
        json_content = await json_file.read()
        data = json.loads(json_content)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON: {e.msg} at line {e.lineno}, column {e.colno}. "
                f"File starts with: {json_content[:80]!r}",
        )

    return data


