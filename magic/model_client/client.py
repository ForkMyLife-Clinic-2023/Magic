import logging
from dataclasses import dataclass
from typing import Dict, List

from aiohttp.client import ClientSession, ClientTimeout
from config import (MAX_TOKENS, MODEL_INSTRUCTION, MODEL_SERVER_URL,
                    REPETITION_PENALTY, TEMPERATURE, TIMEOUT)

logger = logging.getLogger("LLM client")


@dataclass
class ModelMessage:
    role: str
    content: str


class LLMClient:
    def __init__(self, model_name: str, client: ClientSession):
        self._model = model_name
        self._client = client
        self._history = []

    def _update_history(
        self, prompt: List[ModelMessage], response: ModelMessage
    ) -> None:
        prompt.append(response)
        self._history = prompt.copy()

    def _generate_prompt(
        self,
        chosen_company: str,
        user_query: str,
    ) -> List[Dict]:
        """Generate prompt to LLM with instruction (role: system)
        about which company user want to communicate.

        Args:
            chosen_company (str): Name of company chosen by user.
            user_query (str): User message to LLM

        Returns:
            List[Dict]: prepared request body in format for language model.
        """
        prompt = []
        if len(self._history) == 0:
            personalized_instruction = MODEL_INSTRUCTION.replace(
                "__COMPANY__", chosen_company
            )
            prompt.append(
                {
                    "role": "system",
                    "content": personalized_instruction,
                }
            )
        else:
            for message in self._history:
                prompt.append(
                    {
                        "role": message.role,
                        "content": message.content,
                    }
                )
        prompt.append(
            {
                "role": "user",
                "content": user_query,
            }
        )
        return prompt

    async def request_model(self, chosen_company: str, user_query: str) -> ModelMessage:
        """Send request to LLM.

        Args:
            chosed_company (str): Name of company chosen by user.
            query (str): User message to LLM.

        Returns:
            ModelMessage: Object with role and content from model response.
        """
        logger.info(
            f"Service recieved user's query for company {chosen_company}: {user_query}"
        )
        prompt = self._generate_prompt(
            chosen_company=chosen_company,
            user_query=user_query,
        )
        response = await self._client.post(
            url=MODEL_SERVER_URL,
            json=dict(
                model=self._model,
                messages=prompt,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                repetition_penalty=REPETITION_PENALTY,
            ),
            timeout=ClientTimeout(total=TIMEOUT),
        )

        data = await response.json()
        logger.info(f"Recieved data: {data=}")
        message = data["choices"][0]["message"]
        message = ModelMessage(
            role=message["role"],
            content=message["content"],
        )

        self._update_history(prompt=prompt, response=message)

        return message
