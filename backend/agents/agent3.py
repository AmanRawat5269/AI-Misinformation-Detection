from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from agents.agent1 import run_agent1  
from agents.agent2 import run_agent2
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import time
load_dotenv()


def get_verdict(claim):
    start = time.perf_counter()
    agent1_output = run_agent1(claim)
    agent2_results = run_agent2(agent1_output)
    
    
    # extract contexts as plain text list for RAGAS
    contexts = [doc.page_content for doc in agent2_results]

    # formatted contexts for the LLM prompt
    formatted_contexts = "\n\n".join(
        doc.page_content
        for doc in agent2_results
    )
    
    # extract source urls. 
    sources = list(set(
        doc.metadata.get("url", "Unknown")
        for doc in agent2_results
    ))
    
    print(sources)

    
    model = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        max_tokens=550
        )

    template = PromptTemplate(
            template="""
        You are an expert fact-checking assistant.

        CLAIM:
        {agent1_claim}

        EVIDENCE:
        {contexts}

        SOURCE URLS:
        {sources}

        Your job is to determine whether the claim is true, false, or misleading using ONLY the provided evidence.

        Rules:
        1. Use ONLY the provided evidence. Never use your own knowledge.
        2. If the evidence clearly supports the claim, return:
        VERDICT: True
        3. If the evidence clearly disproves or debunks the claim, return:
        VERDICT: False
        4. If the evidence is incomplete, conflicting, weak, or insufficient to confidently judge the claim, return:
        VERDICT: Misleading
        5. Confidence must be between 0.0 and 1.0 and should reflect how strong and reliable the provided evidence is.

        Writing Instructions:
        - Write naturally, as if explaining the result directly to a user.
        - Do NOT mention "the evidence", "the provided context", "Context 1", "Context 2", "according to the retrieved passages", or similar phrases.
        - Do NOT describe your reasoning process.
        - Explain the verdict in simple, easy-to-understand language.
        - Use 4-6 complete sentences.
        - Keep the explanation informative but concise (around 80-120 words).
        - If the claim is false, briefly explain why people commonly believe it if that information appears in the evidence.
        - Do not repeat the claim word-for-word.

        Return EXACTLY in this format:

        VERDICT: <True | False | Misleading>
        CONFIDENCE: <number between 0.0 and 1.0>
        EXPLANATION:
        <4-6 natural sentences written for the user>

        SOURCES:
        <one URL per line copied exactly from the provided source list. If none are available, write "No sources available".>
        """,
            input_variables=["agent1_claim", "contexts", "sources"]
        )
    
    parser = StrOutputParser()

    main_chain = template | model | parser
    
    prompt = template.format(
        agent1_claim=agent1_output["claim"],
        contexts=formatted_contexts,
        sources="\n".join(sources)
    )

    print("Prompt length:", len(prompt))
    print(prompt[:1000])   # first 1000 characters
    
    final_result = main_chain.invoke({
    "agent1_claim": agent1_output["claim"],
    "contexts": formatted_contexts,
    "sources": "\n".join(sources)
    })

    print(f"LLM Verdict: {time.perf_counter()-start:.2f}s")
    print(final_result)
    return final_result, contexts
