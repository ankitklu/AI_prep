from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import os
from dotenv import load_dotenv
load_dotenv()

os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.environ.get("HUGGINGFACEHUB_API_TOKEN", "")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.environ.get("LANGCHAIN_API_KEY", "")

prompt = ChatPromptTemplate.from_messages(
    [
        ("system","You are a helpful assistenat. Please respond to the user request only based on the given context"),
        ("user", "Question: {question}\n Context:{context}")
    ]
)

question = "Can you summarize the speech by Dr APJ Abdul Kalam ?"
context = """I am indeed delighted to be here in Rajkot particularly on the Teacher's Day to address the students and teachers in the meet organized by Mahatma Gandhi Charitable Trust. My greetings to all the children, teachers and the organizers. Mahatma Gandhi was the greatest teacher. During his life time every day he was teaching. Even when he was not with us, his teachings engulf us in every walk of our life. When I am in Rajkot which is very close to where Mahatma Gandhi was born and I am in the place where he had studied in a school, where his marklist is still preserved. I am inspired to walk on the path he had walked. And it is our great fortune that India had such a millennium leader.

In this context Albert Einstien states on Mahatma Gandhi " Generations to come, it may be, will scarecely believe that such a one as this in flesh and blood walked upon this earth". What a great honour Gujarat had attained for having been the home of Mahatma Gandhi. It is all the more important Gujarat continues to walk in the path shown by Gandhiji. My young friends, dream, dream leads to thoughts, and thought leads to action for realizing your mission.

I would like to share with you some of the contributions of great personalities of Gujarat. I would like to present to you three great lives who made a change in our society.

Vision of Nobility

India is indeed fortunate and proud to have Mahatma Gandhiji as 'Father of the nation', who was responsible for getting freedom by his writings and actions, and above all his nobility. When I talk about this great leader with nobility, I would like to go back to my school days at Rameswaram. I would like to narrate one incident to you which fascinated and shaped me when I was a young boy.

On 15th August 1947, my high school teacher Rev. Iyyadorai Solomon took me to hear the mid-night freedom speech of Pandit Jawaharlal Nehru. We were all thrilled when Panditji spoke that the mission was achieved. On the next day, that is on 16th August 1947, I had a great experience. An experience of best of education I can think of. In a Tamil newspaper, on the front page, two news items appeared. One item was India achieving freedom and Panditji's speech. The other news item and the most important one which has been embedded in my memory is about Mahatma Gandhiji walking barefoot in a town in Bengal, removing the pain of riot affected families. Normally as Father of the Nation, Mahatma Gandhi has to be the first to unfurl the national flag on August 15, 1947 in Red Fort. But he was not there at the Red Fort, instead he was at Naokali. Mahatma Gandhi was an embodiment of nobility, elevated thinking and concern for human beings and he was there where there was pain. What an everlasting positive impact of the ideal leadership qualities in the mind of a school boy?

"""


llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen3-8B",
    task="conversational",
    provider="auto",
    max_new_tokens=512,
    temperature=0.01,
)
model = ChatHuggingFace(llm=llm)

output_parser = StrOutputParser()

chain = prompt | model | output_parser

print(chain.invoke({"question": question, "context": context}))


