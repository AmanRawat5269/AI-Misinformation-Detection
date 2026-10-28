
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from agents.agent1 import run_agent1
from agents.agent2 import run_agent2
from langchain_groq import ChatGroq
from langsmith import traceable
from dotenv import load_dotenv

load_dotenv()


@traceable(name="Agent 3 - Context Formatting")
def prepare_contexts(agent2_results):
    # Extract contexts as plain text list for RAGAS
    contexts = [doc.page_content for doc in agent2_results]

    # Format contexts for the LLM prompt
    formatted_contexts = "\n\n".join(
        doc.page_content for doc in agent2_results
    )

    return contexts, formatted_contexts


@traceable(name="Agent 3 - Source Extraction")
def extract_sources(agent2_results):
    # Extract source URLs
    sources = list(set(
        doc.metadata.get("url", "Unknown")
        for doc in agent2_results
    ))

    return sources


@traceable(name="Agent 3 - Prompt Creation")
def create_prompt(claim, formatted_contexts, sources):
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

    prompt = template.format(
        agent1_claim=claim,
        contexts=formatted_contexts,
        sources="\n".join(sources)
    )

    print("Prompt length:", len(prompt))

    return template, prompt


@traceable(name="Agent 3 - Verdict Generation")
def generate_verdict(template, claim, formatted_contexts, sources):
    model = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        max_tokens=550
    )

    parser = StrOutputParser()
    main_chain = template | model | parser

    final_result = main_chain.invoke({
        "agent1_claim": claim,
        "contexts": formatted_contexts,
        "sources": "\n".join(sources)
    })

    print(final_result)
    return final_result


@traceable(name="Agent 3 - Final Verdict")
def get_verdict(claim):
    # Step 1: Run Agent 1
    agent1_output = run_agent1(claim)

    # Step 2: Run Agent 2
    agent2_results = run_agent2(agent1_output)

    # Step 3: Prepare contexts
    contexts, formatted_contexts = prepare_contexts(agent2_results)

    # Step 4: Extract sources
    sources = extract_sources(agent2_results)

    # Step 5: Create prompt
    template, prompt = create_prompt(
        agent1_output["claim"],
        formatted_contexts,
        sources
    )

    # Step 6: Generate verdict
    final_result = generate_verdict(
        template,
        agent1_output["claim"],
        formatted_contexts,
        sources
    )

    return final_result, contexts
