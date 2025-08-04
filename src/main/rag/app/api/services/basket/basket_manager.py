import logging
import os
import re
from typing import List, Optional
import json

from app.api.routers.llm.models import Message
from llama_index.core.prompts import PromptTemplate
from llama_index.core.settings import Settings
from app.api.routers.basket.models import Basket

logger = logging.getLogger("uvicorn")

# CURRENTLY NOT USED

class BasketManager:
    """
    Class to parse structured updates to user basket from the chat response.
    """

    @classmethod
    def get_configured_prompt(cls) -> Optional[str]:
        prompt = os.getenv("UPDATE_BASKET_PROMPT", None)
        if not prompt:
            return None
        return PromptTemplate(prompt)
    
    @classmethod
    async def update_basket_all_messages(
        cls,
        message: str,
        chat_history: List[Message],
        basket: Basket,
    ) -> Basket:
        """
        Update the user basket based on the chat history
        """
        prompt_template = cls.get_configured_prompt()
        if not prompt_template:
            return None

        try:
            conversation = message + "\n"
            for message in reversed(chat_history):
                conversation: str = conversation + f"{message.content}\n"

            # Call the LLM and parse questions from the output
            prompt = prompt_template.format(
                conversation=conversation, 
                basket=basket.model_dump_json()
            )

            logger.info(f"Prompt: {prompt}")

            output = await Settings.llm.acomplete(prompt)
            
            updated_basket_data = cls.extract_json(output.text)

            return Basket(**updated_basket_data)
        
        except Exception as e:
            logger.error(f"Incorrect output format: {e}")
            return None
        
    @classmethod
    def extract_json(cls, text: str):
        match = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)
        json_text = match.group(1) if match else text  # Use raw text if no markdown block
        json_text = json_text.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(json_text)  # Convert to Python dict
        except json.JSONDecodeError:
            return None  # Handle invalid JSON gracefully

    @classmethod
    async def update_basket(
        cls,
        message: str,
        chat_history: List[Message],
        basket: Basket,
    ) -> Basket:
        """
        Update the user basket based on the chat history 
        """

        return await cls.update_basket_all_messages(message, chat_history, basket)
