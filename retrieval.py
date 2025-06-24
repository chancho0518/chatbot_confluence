import os

from dotenv import load_dotenv
from langchain_openai.embeddings.base import OpenAIEmbeddings
from langchain_pinecone.vectorstores import PineconeVectorStore
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken
from confluence import CustomConfluence
from pinecone import PineconeApiException

from openai import Client


load_dotenv()

index_name = "td-docs"

embedding = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=os.getenv('OPENAI_API_KEY'),
)

vectorstore = PineconeVectorStore(
    embedding=embedding,
    index_name=index_name,
    pinecone_api_key=os.getenv('PINECONE_API_KEY'),
)

client = Client(
    api_key=os.getenv('OPENAI_API_KEY')
)

class CustomLoader:
    def __init__(self) -> None:
        self.client = CustomConfluence(
            url="https://alcherainc.atlassian.net",
            username="cr.lee@alcherainc.com",
            password=os.getenv('ATLASSIAN_API_KEY'),
            cloud=True,
        )

    # 토큰측정
    def num_tokens_from_string(self, string: str, encoding_name: str = "cl100k_base") -> int: 
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens
    
    def bootstrap(self):
        documents = []

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,      # 한 청크의 최대 글자 수
            chunk_overlap=200,    # 청크 간 겹치는 글자 수
            length_function=self.num_tokens_from_string,  # 토큰 수 계산 함수
            add_start_index=True, # 청크 시작 부분에 인덱스 추가 여부      
            is_separator_regex=False
        )

        for content in self.client.get_all_page_content('TD'):
            body = content['body']
            metadata = content.copy()
            metadata.pop('body', None)

            if(self.num_tokens_from_string(body)) > 1200:                              
                # 텍스트를 청크로 분할
                chunks = text_splitter.split_text(body)

                # 각 청크를 Document 객체로 변환
                for i, chunk in enumerate(chunks):
                    doc = Document(
                        page_content=chunk,
                        metadata={**metadata, 'insert_id': f"{metadata.get('id', 'no_id')}_{i}"}
                    )
                    documents.append(doc)

            else:
                doc = Document(
                        page_content=body,
                        metadata={**metadata, 'insert_id': f"{metadata.get('id', 'no_id')}_{0}"}
                    )
                documents.append(doc)
        

        # 배치 크기 지정
        batch_size = 50

        # 배치 단위로 업로드
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]

            try:
                vectorstore.add_documents(
                    documents=batch,
                    ids=[doc.metadata['insert_id'] for doc in batch]
                )
            except PineconeApiException as e:
                print(f"상세 오류: {e.body}")  # Pinecone

        
if __name__ == "__main__":
    loader = CustomLoader()
    
    loader.bootstrap()