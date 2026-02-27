from __future__ import annotations

from typing import List
from io import StringIO

import pandas as pd

from storage.artifacts import save_table_csv

async def extract_tables(task_id: str, page) -> List[str]:
    html = await page.content()
    tables = pd.read_html(StringIO(html))
    paths = []
    for idx, table in enumerate(tables):
        path = save_table_csv(task_id, f"table_{idx}", table)
        paths.append(str(path))
    return paths
