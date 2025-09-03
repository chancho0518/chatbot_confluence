__import__('pysqlite3')
import sys
import streamlit as st

from backend import tdbolt
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.base import BaseCallbackHandler

sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# st.title("Sample Confluence 가이드")
st.title("오성화학공업 문서")
st.write("---")

question = st.text_input('질문을 입력하세요')

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, input_text=""):
        self.container = container
        self.input_text = input_text
        
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)
   
    if st.button('질문하기'):
        if not question:
            st.error("질문을 입력해주세요.")
        else:
            placeholder = st.empty()
            placeholder.write("질문을 처리하는 중입니다... 잠시만 기다려주세요.")
            
            with st.spinner('질문을 처리하는 중...'):
                response = tdbolt().invoke(question)
                
            placeholder.empty()  # 메시지 삭제
            st.write(response)