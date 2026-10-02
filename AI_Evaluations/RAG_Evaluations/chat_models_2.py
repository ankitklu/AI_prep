import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from rag_imp_1 import retriever

load_dotenv()

llm = init_chat_model("groq:openai/gpt-oss-20b", temperature=0.1)


from langsmith import traceable

@traceable()
def rag_bot(question:str)->dict:
    ## Relevant context
    docs=retriever.invoke(question)
    docs_string = " ".join(doc.page_content for doc in docs)

    instructions = f"""You are a helpful assistant who is good at analyzing source information and answering questions.       Use the following source documents to answer the user's questions.       If you don't know the answer, just say that you don't know.       Use three sentences maximum and keep the answer concise.

Documents:
{docs_string}"""
    
    ## llm invoke

    ai_msg=llm.invoke([
         {"role": "system", "content": instructions},
        {"role": "user", "content": question},

    ])
    return {"answer":ai_msg.content,"documents":docs}

print(rag_bot("What are agents ?")["answer"])