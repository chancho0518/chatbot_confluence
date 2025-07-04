import os

from langchain_openai.chat_models import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.output_parsers.string import StrOutputParser

from retrieval import vectorstore

model = ChatOpenAI(
    model="gpt-4o",
    api_key=os.getenv('OPENAI_API_KEY'),
    temperature=0.8,
    max_tokens=2500,
)

def tdbolt():
    with open('system_prompt.md', 'r', encoding='utf-8') as f:
        system_prompt = f.read()
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{query}"),
        ]
    )
    retriever = vectorstore.as_retriever(
        # search_type='similarity',
        search_kwargs={
            'k': 8
        }
    )
    parser = StrOutputParser()

    def format_documents(docs: list):
        formatted_docs = '\n\n---\n\n'.join(
            f'Title: {doc.metadata.get("title")}\n'
            f'Page Content: """{doc.page_content}"""\n'
            f'Source Link: {doc.metadata.get("link", "")}\n'
            for doc in docs
        )

        if not formatted_docs:
            formatted_docs = "No relevant documents found."
        else:
            formatted_docs = f"Relevant Documents:\n\n{formatted_docs}"

        return formatted_docs

    return {
        'documents': retriever | format_documents, 
        'query': RunnablePassthrough()
        } | prompt | model | parser