import json
from typing import Any

import httpx


async def project_manager_agent(task_description: str) -> dict[str, Any]:
    """
    Принимает описание задачи, возвращает разбивку на подзадачи + лог рассуждений.
    Использует Ollama.
    """
    prompt = f"""
Ты — Project Manager Agent. Пользователь дал задачу:

"{task_description}"

Твоя задача:
1. Подумай шаг за шагом: как реализовать эту задачу?
2. Разбей её на 3–5 логических подзадач.
3. Верни ОТВЕТ ТОЛЬКО В ФОРМАТЕ JSON, без пояснений до или после.

Формат ответа:
{{
  "reasoning_log": ["Шаг 1: ...", "Шаг 2: ..."],
  "subtasks": [
    {{"id": 1, "title": "Краткое название", "description": "Подробное описание"}},
    ...
  ]
}}
"""

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "gemma3:1b",
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                },
            )
            response.raise_for_status()
            result = response.json()
            output_text = result.get("response", "{}")
            return json.loads(output_text)
    except Exception as e:
        return {
            "reasoning_log": [f"Ошибка при вызове LLM: {str(e)}"],
            "subtasks": [
                {
                    "id": 1,
                    "title": "Ошибка генерации",
                    "description": "Не удалось разбить задачу. Проверьте, запущен ли Ollama.",
                }
            ],
        }
