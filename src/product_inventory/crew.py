from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai_tools import PDFSearchTool
from tools.custom_tool import ShoppingAPITool, SearchWebTool, SearchImageTool
# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class ProductInventory():
	"""ProductInventory crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'
	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools


	@agent
	def front_end_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['front_end_agent'],
			llm=LLM(model="azure/gpt-4o-mini-global"),
			verbose=True,
			tools=[ShoppingAPITool()]
		)# type: ignore

	@agent
	def product_search_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['product_search_agent'],
			llm=LLM(model="azure/gpt-4o-mini-global"),
			verbose=True,
			tools=[SearchWebTool()]
		)# type: ignore
	
	@agent
	def image_search_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['image_search_agent'],
			llm=LLM(model="gemini/gemini-1.5-pro-latest",temperature=0.7),
			verbose=True,
			tools=[SearchImageTool()]
		)# type: ignore

	@agent
	def customer_service_representative_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['customer_service_representative_agent'],
			llm=LLM(model="azure/gpt-4o-mini-global"),
			tools = [PDFSearchTool(pdf = r'C:\Users\saahil.ali\OneDrive - Accenture\KT Documents\crewAI\Productdetails.pdf')],
			verbose=True
		) # type: ignore
	


	
	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def list_products_task(self) -> Task:
		return Task(
			config=self.tasks_config['list_products_task'],
		)# type: ignore

	@task
	def add_item_to_cart_task(self) -> Task:
		return Task(
			config=self.tasks_config['add_item_to_cart_task'],
		)# type: ignore
	
	@task
	def search_product_task(self) -> Task:
		return Task(
			config=self.tasks_config['search_product_task'],
		)# type: ignore
	
	@task
	def image_search_task(self) -> Task:
		return Task(
			config=self.tasks_config['image_search_task'],
		)# type: ignore
	
	@task
	def customer_service_task(self) -> Task:
		return Task(
			config=self.tasks_config['customer_service_task'],
		)# type: ignore


	@crew
	def crew(self) -> Crew:
		"""Creates the ProductInventory crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
	
	@before_kickoff
	def before_kickoff_function(self, inputs):
		print(f"Before kickoff function with inputs: {inputs}")
		return inputs # You can return the inputs or modify them as needed

	@after_kickoff
	def after_kickoff_function(self, result):
		print(f"After kickoff function with result: {result}")
		return result # You can return the result or modify it as needed
