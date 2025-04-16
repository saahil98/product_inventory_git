from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai_tools import PDFSearchTool
from pydantic import BaseModel
from tools.custom_tool import ShoppingAPITool, SearchWebTool, SearchImageTool, \
	JsonReadTool, GetSchemaTool, DatabaseTool
import os
from pydantic_model import MeetingPlan
from dotenv import load_dotenv
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
	dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.env'))
	load_dotenv(dotenv_path=dotenv_path)
	azure_llm = LLM(model=os.getenv("model"), 
				temperature=0.7, 
				base_url=os.getenv("AZURE_API_BASE"), 
				api_version=os.getenv("AZURE_API_VERSION"), 
				api_key=os.getenv("NEW_AZURE_API_KEY"), 
				api_base=os.getenv("AZURE_API_BASE"))
	# model=os.getenv("model")
	# base_url=os.getenv("AZURE_API_BASE")
	# api_version=os.getenv("AZURE_API_VERSION")
	# api_key=os.getenv("NEW_AZURE_API_KEY")
	# api_base=os.getenv("AZURE_API_BASE")

	# print("CONFIG DETAILS: ",model, base_url, api_version, api_key, api_base)
	@agent
	def manager_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['manager_agent'],
			llm=self.azure_llm,
			allow_delegation=False,
			max_iter=3,
			max_execution_time=40,
			verbose=True
		)# type: ignore

	@agent
	def front_end_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['front_end_agent'],
			llm=self.azure_llm,
			verbose=True,
			tools=[ShoppingAPITool()],
			allow_delegation=False
		)# type: ignore

	@agent
	def product_search_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['product_search_agent'],
			llm=self.azure_llm,
			verbose=True,
			tools=[SearchWebTool()],
			allow_delegation=False
		)# type: ignore
	
	@agent
	def image_search_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['image_search_agent'],
			llm=LLM(model="gemini/gemini-1.5-pro-latest",temperature=0.7),
			verbose=True,
			tools=[SearchImageTool()],
			allow_delegation=False
		)# type: ignore

	@agent
	def pdf_search_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['pdf_search_agent'],
			llm=self.azure_llm,
			tools = [PDFSearchTool(pdf = r'C:\Users\saahil.ali\OneDrive - Accenture\KT Documents\crewAI\Productdetails.pdf')],
			max_iter=3,
			verbose=True,
			allow_delegation=False
		) # type: ignore

	#Priyanka's Agents
	# Postgres DB agents

	@agent
	def read_data_agent(self) -> Agent:
		return Agent(
         config=self.agents_config['read_data_agent'],
         verbose=True,
         allow_delegation=False,
         tool=[JsonReadTool()],
         llm=self.azure_llm,
         )# type: ignore
	
	@agent
	def schema_analyzer(self) -> Agent:
		return Agent(
         config=self.agents_config['database_schema_analyzer'],
         verbose=True,
         allow_delegation=False,
         tools=[GetSchemaTool()],
         llm=self.azure_llm
         )# type: ignore
    
	@agent
	def query_generator(self) -> Agent:
		return Agent(
         config=self.agents_config['database_query_generator'],
         verbose=True,
         allow_delegation=False,
         llm=self.azure_llm
         )# type: ignore
    
	@agent
	def query_executor(self) -> Agent:
		return Agent(
         config=self.agents_config['database_query_executor'],
         verbose=True,
         allow_delegation=False,
         tools=[DatabaseTool()],
         llm=self.azure_llm
         )# type: ignore


	
	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def manager_task(self) -> Task:
		return Task(
			config=self.tasks_config['manager_agent_task'],
			output_pydantic=MeetingPlan,
		)# type: ignore

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
	def pdf_search_task(self) -> Task:
		return Task(
			config=self.tasks_config['pdf_search_task'],
		)# type: ignore

	#Priyanka's Tasks
	# Database tasks
	
	@task
	def read_data_task(self) -> Task:
		return Task(
         config=self.tasks_config['read_data_task'],
         function_args={'file_path': '{file_path}'}
         )
    
	@task
	def schema_task(self) -> Task:
		return Task(
         config=self.tasks_config['schema_task']
         )

	@task
	def query_generation(self) -> Task:
		return Task(
         config=self.tasks_config['query_generator_task']
         )
    
	@task
	def query_execution(self) -> Task:
		return Task(
         config=self.tasks_config['query_executor_task'],
         func_args = {'query':'{query_generation.output}'}
         )

	# @crew
	# def crew(self) -> Crew:
	# 	"""Creates the ProductInventory crew"""
	# 	# To learn how to add knowledge sources to your crew, check out the documentation:
	# 	# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

	# 	return Crew(
	# 		agents=self.agents, # Automatically created by the @agent decorator
	# 		tasks=self.tasks, # Automatically created by the @task decorator
	# 		manager_agent=self.manager_agent(),
	# 		# manager_llm= self.azure_llm,
	# 		# process=Process.sequential,
	# 		verbose=True,
	# 		process=Process.hierarchical # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
	# 	)
	
	# @before_kickoff
	# def before_kickoff_function(self, inputs):
	# 	print(f"Before kickoff function with inputs: {inputs}")
	# 	return inputs # You can return the inputs or modify them as needed

	# @after_kickoff
	# def after_kickoff_function(self, result):
	# 	print(f"After kickoff function with result: {result}")
	# 	return result # You can return the result or modify it as needed
