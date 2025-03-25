from crewai import Agent, Task
from crewai.flow.flow import Flow, listen, start
from typing import cast, List
from crewai_tools import PDFSearchTool
from tools.custom_tool import ShoppingAPITool, SearchWebTool, SearchImageTool, \
	JsonReadTool, GetSchemaTool, DatabaseTool
from pydantic_model import MeetingPlan, CustomerServiceState
from llm import azure_llm

def product_list_flow(question: str) -> str:
    agent = Agent(
        role="Customer Receptionist",
        goal=f"""You are a front end agent you are having two tasks 
                1. List the products - List Products Task 
                2. Add the product to the cart - Add Item to Cart Task 
                based on the user query {question} execute ONLY the appropriate task 
                and give the output. 
                Any irrelevant query apart from the above mentioned crew task do not run any task under you.""",
        backstory="""You are a skilled customer receptionist specializing in store product management. 
                    Your primary role is to fetch and relay store product details and cart updates using the API tool. 
                    You efficiently process requests and ensure accurate responses to the manager agent.""",
        llm=azure_llm,
        allow_delegation=False,
        max_iter=3,
        max_execution_time=40,
        verbose=True,
        tools=[ShoppingAPITool()],
    )
    task = Task(
        description="""The customer has asked for the list of products available in the store.  
                - For retrieving the product list, call the API with the following details: 
                - Endpoint: `products` 
                - Method: `GET` 
                - Request Body: '' 
                - Extract only the product list from the JSON response returned by the API and present it as a JSON object. 
                - If the product list is empty, inform the customer that no products are currently available.""",
        expected_output="""A JSON object containing the products list with product id, product name, brand, model and price""",
        agent=agent
    )
    opinion = task.execute_sync()
    return opinion.raw

def adding_to_cart_flow(question: str) -> str:
    agent = Agent(
        role="Customer Receptionist",
        goal=f"""You are a front end agent you are having two tasks 
                1. List the products - List Products Task 
                2. Add the product to the cart - Add Item to Cart Task 
                based on the user query {question} execute ONLY the appropriate task 
                and give the output. 
                Any irrelevant query apart from the above mentioned crew task do not run any task under you.""",
        backstory="""You are a skilled customer receptionist specializing in store product management.
                    Your primary role is to fetch and relay store product details and cart updates using the API tool. 
                    You efficiently process requests and ensure accurate responses to the manager agent.""",
        llm=azure_llm,
        allow_delegation=False,
        max_iter=3,
        max_execution_time=40,
        verbose=True,
        tools=[ShoppingAPITool()],
    )
    task = Task(
        description=f"""
    Analyze the customer's query: {question} to determine if they are requesting to add specific products with a given quantity to the cart. 
    - First, check if the requested products exist in the product list by calling the API tool: 
    - Endpoint: `products` 
    - Method: `GET` 
    - Request Body: '' 
    - If the API response contains the product list, create JSON output keys ProdID, Qty. 
    - If multiple products are requested, ensure each product ID is mapped correctly with the requested quantity in a structured JSON format. 
    - If a product is not found in the product list, respond to the customer with an appropriate message indicating that the item is unavailable. 
    - Add only the available items to the cart. 
    - Call the 'Add to Cart' API with the captured product details: 
    - Endpoint: `cart` 
    - Method: `POST` 
    - Request Body: JSON containing the product ID and quantity.""",
    expected_output="""A JSON response displaying the items added to the cart, structured as: 
    [{ ProdID: <product_id>, Qty: <quantity> }], 
    along with the API response from the API tool.""",
    agent=agent
    )
    opinion = task.execute_sync()
    return opinion.raw

def web_search_flow(question: str) -> str:
    agent = Agent(
        role="Product Search Agent",
        goal=f"""
            Search for products on the Internet by using the 'Internet Search' tool. 
            Make sure the input of the tool should be the product name 
            extract the product name from the query : {question}. 
            After extraction of the product name pass in the tool.
            based on the output given by the tool, return the three best price found for the product. 
            """,
        backstory="""
            I am a product search agent that can help you find product's best price on the Internet.
            """,
        llm=azure_llm,
        allow_delegation=False,
        max_iter=3,
        max_execution_time=40,
        verbose=True,
        tools=[SearchWebTool()],
    )
    task = Task(
        description=f"""
            An user reached out with a query: {question}
            please search the internet for the product's best price.
            Use the 'Internet Search' tool to search for the product and find the best price.
            pass the query
            Return the three best price found for the product.
            """,
        expected_output="A List of three sources with the best price for the product.",
        agent=agent
    )
        
    opinion = task.execute_sync()
    return opinion.raw

def manager(team: str, query: str) -> List[str]:
    agent = Agent(
        role="Customer Support Manager",
        goal="Select the best team members for customer "
            "support meetings to resolve customer issues efficiently.",
        backstory="You are an experienced customer support "
                "manager with a proven track record of leading "
                "high-performing support teams and resolving "
                "complex customer issues effectively.",
        llm=azure_llm,
        allow_delegation=False,
        max_iter=3,
        max_execution_time=40,
        verbose=True
    )
    task = Task(
        description=f"""Analyze the customer's ticket and determine 
                        which specialists from your team should attend 
                        a meeting to address the issue. Provide only a 
                        list of names. 
                        If the query is about listing the products or adding to cart then delegate the task to product_list_flow or adding_to_cart_flow 
                        If the query is about searching the product on the internet then delegate the task to web_search_flow
                        Exclude experts who are not 
                        relevant. If no specialist is needed, return an empty list.
                        Team: {team},  Query: {query}
                    """,
        expected_output="List of names of relevant experts from "
                        "the team or an empty list if no expert is needed.",
        agent=agent,
        output_pydantic=MeetingPlan,
    )
    meeting = task.execute_sync()
    if meeting.pydantic:
        meeting.pydantic = cast(MeetingPlan, meeting.pydantic)
        return meeting.pydantic.chosen_specialists
    else:
        raise ValueError("Invalid list of specialists: {meeting.raw}")


class CustomerServiceFlow(Flow[CustomerServiceState]):
    available_specialists = {
        'product_list_flow': product_list_flow,
        'adding_to_cart_flow': adding_to_cart_flow,
        'web_search_flow': web_search_flow
    }

    @start()
    def schedule_meeting(self):
        print(f"list of available specialists: {self.available_specialists.keys()}")
        team = ', '.join(
            [repr(name) for name in self.available_specialists.keys()]
        )
        query = self.state.query
        chosen_specialists = manager(team, query)
        self.state.chosen_specialists = chosen_specialists

    @listen(schedule_meeting)
    def conduct_meeting(self):
        opinions: List[str] = []
        for specialist in self.state.chosen_specialists:
            try:
                opinion = self.available_specialists[specialist](
                    self.state.query
                )
                opinions.append(f"{specialist} stated: {opinion}")
            except:
                print(f"\nError: '{specialist}' key is not available.\n")
                continue
        self.state.opinions = opinions
        return opinions

if __name__ == '__main__':
    question = input("[🤖 Help Desk]: Hi! How can I help you today?\n")
    flow = CustomerServiceFlow()
    result = flow.kickoff(
        inputs = {
        'query': question,
        }
    )
    print(f"\n[🤖 Final Answer]:\n{result}")
    print(f"\n[🤖 Flow State]:\n{flow.state}\n")