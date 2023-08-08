from langchain import OpenAI, PromptTemplate
from langchain.chains import LLMChain
import chainlit as cl
from decouple import config


def chain_builder() -> LLMChain:
    '''Used to intantiate the chain for that user session'''
    template = """You are a very good historian who knows all about world history.
    
    Question: {question}

    Answer: """

    prompt = PromptTemplate(template=template, input_variables=["question"])

    llm = OpenAI(
        temperature=0.6,
        openai_api_key=config("OPENAI_API_KEY"),
    )

    chain = LLMChain(prompt=prompt, llm=llm)

    return chain


@cl.on_chat_start
async def start() -> None:
    msg = cl.Message(content="Loading, Please wait...")
    await msg.send()
    # display this once the page loads successfully.
    msg.content = "Hello there, welcome to your personal History teacher"
    # update the loading msg
    await msg.update()

    # get the chain object
    chain = chain_builder()

    # Store chain in the user session
    cl.user_session.set("chain", chain)


@cl.on_message
async def main(message: str) -> None:
    # Retrieve the chain from the user session
    chain = cl.user_session.get("chain")

    # create callback
    callback = cl.AsyncLangchainCallbackHandler()

    # Call the chain asynchronously
    res = await chain.acall(message, callbacks=[callback])

    # Do any post processing here

    # Send the response
    await cl.Message(content=res["text"], author="Code With Prince").send()
