from crewai import LLM

azure_llm = LLM(
    model='azure/gpt-4o-mini',
    temperature=0.7,
)

gemini_llm = LLM(
    model="gemini/gemini-1.5-pro-latest",
    temperature=0.7
)