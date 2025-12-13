from langchain_core.prompts import ChatPromptTemplate

def create_prompt():
    return ChatPromptTemplate.from_messages([
        ("system", "### Справочная информация\n{rag}"),
        ("placeholder", "{messages}")
    ])