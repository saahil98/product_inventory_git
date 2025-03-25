from crewai import LLM

azure_llm = LLM(
    model='azure/gpt-4o-mini',
    temperature=0.7,
	max_tokens=512
)