from api.utils.llm import LLM
from api.database.database import add_messages_to_chat_history, get_chat_history
from api.utils.vectorstore import create_vectorstore, query_vectorstore
from langchain.messages import HumanMessage, AIMessage
import base64

from prompts.main_prompt import create_prompt

async def run_llm_pipeline(
        dialog_id: str, 
        query: str = "", 
        picture: bytes | None = None
    ) -> AIMessage:
    dialog_id = str(dialog_id)
    vectorstore = create_vectorstore(dialog_id)
    rag = await query_vectorstore(vectorstore, query)
    messages = await get_chat_history(dialog_id)
    try:
        message = {
            "role": "user",
            "content": [
                {"type": "text", "text": query},
            ]
        }
        if picture:
            base64_image = base64.b64encode(picture).decode('utf-8')
            message["content"].append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            )
        prompt = create_prompt()
        messages.append(message) # type: ignore
        answer = await (prompt | LLM).ainvoke(
            {"messages": messages, "rag": rag}
        )
    except:
        answer = AIMessage("Произошла ошибка повторите запрос позже")
    await add_messages_to_chat_history(
        dialog_id,
        [
            HumanMessage(query),
            answer
        ])
    return answer