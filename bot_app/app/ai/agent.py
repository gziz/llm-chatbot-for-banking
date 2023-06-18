import json
from typing import List, Tuple

from openai import ChatCompletion
from pydantic import BaseModel

from ..schemas import AiChatMessage
from ..utils import logger
from .prompts_en import PROMPTS
from .vecstores import Vecstores


class Agent:
    def __init__(self):
        self.vecstore = Vecstores()
        self.total_tokens = 0

    def __call__(self, profile: int, user_msg: str, history: List[str]) -> Tuple[AiChatMessage]:
        """
        Generate AI response for the given user message and history.

        :param user_msg: User's message
        :param history: Chat history
        :return: Tuple of User's message, AI message and AI's message as a string.
        """

        user_msg = self.amplify_msg(user_msg, history)

        context, metadatas = self.get_context(user_msg, profile)

        history = self.format_history(history)
        prompt = PROMPTS[f"GET_INFO_{profile}"].format(
            user_msg=user_msg, context=context, history=history
        )

        ai_msg = self.chat_completion(prompt)

        return (
            AiChatMessage(**{"role": "user", "content": user_msg}),
            AiChatMessage(**{"role": "assistant", "content": ai_msg}),
            ai_msg,
        )

    def amplify_msg(self, user_msg: str, history: List[str]) -> str:

        history = self.format_history(history, 2)

        prompt = PROMPTS["AMPLIFY_QUERY"].format(
            chat_history=history, user_msg=user_msg
            )
        
        logger.info(prompt)
        user_msg = self.chat_completion(prompt)

        logger.info(f"Amplified msg: {user_msg}")
        return user_msg


    def get_context(self, q: str, profile: str) -> Tuple:
        """
        Get context for a given query and topic.

        :param q: User's query
        :param topic: Topic string
        :return: Context and metadata
        """

        documents = self.vecstore.similarity_search(q, profile)

        metadatas = [doc.metadata["source"] for doc in documents]
        raw_context = "\n\n".join([doc.page_content for doc in documents])

        context = PROMPTS["CONTEXT"].format(raw_context=raw_context)

        return (context, metadatas)

    def format_history(self, history: List[str], last_k_msg: int = 0) -> str:
        """
        Format history list as a string.

        :param history: Chat history
        :param k: Ge
        :return: Formatted history string
        """
        # Get the last k messages
        start = 0 if last_k_msg == 0 else max(len(history) - last_k_msg, 0)
        return "\n".join([m for m in history[start: ]])
        


    def chat_completion(self, prompt: str, max_tokens: int = None) -> str:
        """
        Get AI response for a given prompt.

        :param prompt: Prompt for the AI
        :param max_tokens: Maximum tokens for the response
        :return: AI's response
        """
        response = ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens)
            
        self.total_tokens += response["usage"]["total_tokens"]
        return response['choices'][0]['message']['content']
    