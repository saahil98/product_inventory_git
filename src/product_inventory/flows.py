from crewai import Agent, Task
from crewai.flow.flow import Flow, listen, start
import sys
import os
sys.path.append((os.path.dirname(os.path.abspath(__file__))))

from typing import cast, List
import os
from crewai_tools import PDFSearchTool
from tools.custom_tool import ShoppingAPITool, SearchWebTool, SearchImageTool, \
	JsonReadTool, GetSchemaTool, DatabaseTool
from pydantic_model import MeetingPlan, CustomerServiceState, Cart
from llm import azure_llm, gemini_llm, openai_llm

def product_list_flow(question: str, **kwargs) -> str:
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

def adding_to_cart_flow(question: str, **kwargs) -> str:
    agent = Agent(
        role="Cart Addition Receptionist",
        goal=f"""You are a Cart addition agent you are having three tasks 
                1. List the products - using api tool 
                2. Add the product to the cart - usin api tool
                3. Generate an output .json file under '/data' folder 
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
    - Request Body: JSON containing the product ID and quantity.
    - Extract the items added to the cart from the API response and structure them as a JSON object.
    - Save the output JSON file under the '/data' folder with the name 'cart_output.json'.
    """,
    expected_output="""A JSON file under folder '/data' displaying the items added to the cart, structured as: 
    [
        {
            "productid": "<product_id>",
            "productmodelnumber": "",  
            "productprice": "",
            "productquantity": "<quantity>"
        },
        ...
    ]
    along with the API response from the API tool.""",
    agent=agent,
    output_pydantic= Cart,
    output_file=os.path.join(os.path.dirname(__file__), 'data', 'cart_output.json')
    )
    opinion = task.execute_sync()
    return opinion.raw

def web_search_flow(question: str, **kwargs) -> str:
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

def image_search_flow(question: str, **kwargs) -> str:
    image_path = kwargs.get("image_path")
    agent = Agent(
        role="Product Image Search Assistant",
        goal=f"""You are a specialized agent capable of performing image-based product searches.
            Given an image and a prompt from task description, use the image search tool to identify the product
            and return the search results to the user.
            The tool accepts two parameters {question} and {image_path}""",
        backstory="""You are an expert in image-based product retrieval, leveraging AI-powered search tools to find products efficiently.""",
        allow_delegation=False,
        max_iter=3,
        max_execution_time=40,
        verbose=True,
        llm= gemini_llm,
        tools=[SearchImageTool()],
    )
    task = Task(
        description=f"""
                do an image search and find what kind of product is in the image
                prompt = Extract the object name from the image. If the object matches any item from the list ['Refrigerator', 'Washing Machine', 'Camera'], use the corresponding name. Otherwise, label the object as 'Others'
                image_path = {image_path}
                - Use the image search tool with the given prompt and image path. 
                - Extract and format the response from the tool.
    """,
        expected_output="A list of search results based on the image provided.",
        agent=agent
    )
    opinion = task.execute_sync()
    return opinion.raw

def pdf_search_flow(question: str, **kwargs) -> str:
    pdf_path = kwargs.get("pdf_path")
    print(f"pdf_path: {pdf_path}")
    print(f"type of pdf_path: {type(pdf_path)}")


    agent = Agent(
        role="PDF Search Specialist",
        goal=f"Search for information in the PDF document as per the user query: {question}",
        backstory="""You are a PDF search specialist who can extract information from PDF documents. 
                    You use the PDF search tool to find relevant data based on the user query.""",
        allow_delegation=False,
        max_iter=3,
        max_execution_time=40,
        verbose=True,
        llm=openai_llm,
        tools=[PDFSearchTool(pdf=pdf_path)],
    )
    task = Task(
        description=f"""
    Search for the information in the PDF document as per the user query: {question}
    - Use the PDF search tool to find the relevant data in the PDF document.
    - Extract and format the response from the tool.
    """,
    expected_output="The extracted information from the PDF document based on the user query.",
    agent=agent
    )
    opinion = task.execute_sync()
    return opinion.raw

# Added db agents

def read_data_agent_flow(question: str, **kwargs) -> str:
    json_file_path = kwargs.get("json_path")
    agent = Agent(
    role="Data Reading Specialist",
    goal=f"Process requests for reading data from JSON files as specified in {json_file_path}.",
    backstory="""Focused on extracting and presenting data, this agent uses JSONSearchTool
                to effectively read and parse JSON file data.""",
    llm=azure_llm,
    allow_delegation=False,
    max_iter=3,
    max_execution_time=40,
    verbose=True,
    tools=[JsonReadTool()],
    )

    task = Task(
    description=f"""
    USe JsonReaderTool to Read the {json_file_path} file and extract the data.
    """,
    expected_output="Json data from the json file",
    agent=agent
    )
    opinion = task.execute_sync()
    return opinion.raw

def schema_analyze_flow(question: str, **kwargs) -> str:
    db_connection = kwargs.get("database_connection")
    table=kwargs.get("table")
    schema_analyzer = Agent(
    role='Schema Analyzer',
    goal='Get database schema',
    backstory="""You are an expert database developer who understands PostgreSQL schemas 
                    and data structures. """,
    llm=azure_llm,
    allow_delegation=False,
    max_iter=5,
    verbose=True,
    max_execution_time=40,
    tools=[GetSchemaTool()]
    )
    
    task =Task(
    description=f"""
    Connect to the  given {db_connection} database and {table} table, get the database schema and return the schema.
    Connect to the given database get the database schema and return the schema.{db_connection}
    """,
    expected_output="Database schema",
    agent=schema_analyzer
        )    
    opinion = task.execute_sync()
    return opinion.raw

def query_generator_flow(question: str, **kwargs) -> str: 
    last_agent_output = kwargs.get("last_agent_output")
    if len(last_agent_output)>1:
        json_data = last_agent_output[-2]
        json_data=json_data.split(" ")[2:]
        json_data = " ".join(json_data)
        print(json_data, "json_data after splitting")
    else:
        json_data = None
    query =question
    table = kwargs.get("table")
    agent = Agent(
    role='Query Generator',
    goal=f'Generate Postgres SQL queries to insert, fetch or update data based on {query} user query',
    backstory="""You are an expert at generating Postgres SQL queries based on user query and database schema.
    You validate queries before execution and ensure safe database operations.""",
    # tools=[tool],
    max_iter=7,
    verbose=True,
    # max_execution_time=40,
    llm=azure_llm
        )
    
    task = Task(
    description=f"""
    Generate a PostgreSQL query based on:
    1. User request: {query}
    2. Consider  data: {json_data} to insert the data
    2. Target table: {table}
    3. {last_agent_output[-1]} Database schema from the schema_analyze_flow task
    
    Requirements:
    1. Generate a syntactically correct PostgreSQL query for a {query} user request
    2. If query contains to generate bill number write insert query  to insert the data into the {table} table, 
    if data contains multiple products then insert all the products in the table
    3. If query contains to fetch the data from the table write select query and fetch the data from the {table} table for a given column
    4. If the query is to update the data in the table write update query and update the data in the {table} table for a given column
    5. Include proper table name and column names
    6. Don't consider transaction id from the data, ignore transid column for inserting
    7. Add appropriate WHERE clauses if needed
    9. Ensure the query is safe and follows best practices
    
    The query will be executed by the query executor task.
    """,
    expected_output="A valid PostgreSQL query string",
    agent=agent

    )
    opinion = task.execute_sync()
    return opinion.raw

def query_executor_flow(question: str, **kwargs) -> str:
    # question = kwargs.get("sql_query")
    query = question
    last_agent_output = kwargs.get("last_agent_output")
    db_connection=kwargs.get("database_connection")
    #for debugging 
    print(f"last_agent_output: {last_agent_output}")
    agent = Agent(
    role='Query Executor',
    goal='Execute the provided Postgres SQL query accurately and return results',
    backstory="""You are an expert database query executor. You take Postgres SQL queries, 
    execute them safely, and return well-formatted results. You carefully validate 
    queries before execution and ensure proper error handling.""",
    tools=[DatabaseTool()],
    llm=azure_llm,
    verbose=True,
    # max_iter=7,
    # max_execution_time=40
    )
    task = Task(
    description=f"""
    Execute the provided Postgres SQL query following these steps:
    The tool accepts two parameters query = {last_agent_output} and db_uri ={db_connection}
    1. Review the query received from the query generator
    2. Validate the query structure and safety
    3. Execute the query using the database tool
    4. Format and return the results in a clear, readable format. 
    5. Articulte the result  to answer the user query {query}
    
    Context:

    - Generated Query: {last_agent_output}
    
    Important:
    - Ensure the query is properly formatted before execution
    - Handle any potential errors gracefully
    - Return results in a structured format
    """,
    expected_output="""A dictionary containing:
    1. The status of the query execution
    2. if the query is select query then return the data, if the query is insert return the billnumbers it has inserted , 
      if update return the updated data the updated bill numbers. If there are multiple bill amount for same bill number sum it and provide total amount.
      Format the result to answer for a {query} user query
    3. message
    """,
   
    tools=[DatabaseTool()],
    agent=agent,
    # function_args={'query': last_agent_output, 'db_uri': db_connection}
    )
    opinion = task.execute_sync()
    return opinion.raw

def manager(team: str, query: str) -> List[str]:
    agent = Agent(
        role="Customer Support Manager",
        goal=f"""
            Select the best specialist for customer's query: '{query}' 
            support meetings to resolve customer issues efficiently.
            """,
        backstory="""You are an experienced customer support 
                manager with a proven track record of leading 
                high-performing support teams and resolving 
                complex customer issues effectively.""",
        llm=azure_llm,
        allow_delegation=False,
        # max_iter=5,
        # max_execution_time=60,
        verbose=True
    )
    task = Task(
        description=f"""
                Analyze the customer's Query : ' {query} ' and determine 
                which specialists from your team should attend 
                a meeting to address the issue. Provide only list of names. 
                If the query is about listing the products then choose specialist product_list_flow 
                If the query is about adding the product to the cart then choose specialist adding_to_cart_flow 
                If the query is about searching the product on the internet then choose specialist web_search_flow 
                If the query is about searching the product image then choose specialist image_search_flow
                If the query is about finding similarities with the image and product list then choose specialist image_search_flow and product_list_flow
                If the query is about referring catalog, pdf document, document then choose specialist pdf_search_flow
                If the query is about reading the data from json file then choose specialist read_data_agent_flow
                If the query is about fetching the data from database or updating the data
                then choose this series of specialist [schema_analyze_flow, query_generator_flow, query_executor_flow]
                If the query is about generating the data or creating or inserting the data into database 
                then choose this series of specialist [read_data_agent_flow, schema_analyze_flow, query_generator_flow, query_executor_flow]  
                If the query is not related to any of the above queires then do not choose any specialist reutun an empty list.
                Exclude experts who are not relevant. If no specialist is needed, return an empty list.
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

def client_outcome_architect(question: str, opinions: str) -> str:
    agent = Agent(
        role="Customer Response Architect",
        goal=f"""Craft helpful json responses from specialists / agents opinions : {opinions}. 
                follow the task description properly and generate a response
                """,
        backstory="Expert in customer service and synthesizing "
                  "information to create clear, friendly replies.",
        llm=azure_llm,
        allow_delegation=False,
        max_iter=2,
        max_execution_time=30,
        verbose=True
    )
 
    task = Task(
        description=f"""Generate customer response from the customer question: {question} and 
                    Classify the response in JSON format and add below attributes, follow the format below
        
                    message: <generate a reponse based on the user query : {question} and also on opinion: {opinions} from last agent>
                    data: <reponse from the last agent refer {opinions}>
                    status: <success or failure> determine based on the response from the last agent 

                    Rely on expert input only. Answer in 
                    500 characters or less. If no input or question not related to
                    product, search, billing or cart the say: 
                    message : I'm sorry, the question is not relevant to our team.
                    data : <return as blank python list> []
                    status: failed
                    """,
        expected_output=f"""
                        A JSON object with the following attributes:

                        status: <success or failure> determine based on the response from the last agent
                        message: <generate a reponse based on the user query : {question} and also on opinion from last agent {opinions}>
                        data: <reponse from the last agent refer {opinions} for the last agent output>
                    
                        """,
        agent=agent
    )
    outcome = task.execute_sync()
    return outcome.raw

class CustomerServiceFlow(Flow[CustomerServiceState]):
    available_specialists = {
        'product_list_flow': product_list_flow,
        'adding_to_cart_flow': adding_to_cart_flow,
        'web_search_flow': web_search_flow,
        'image_search_flow': image_search_flow,
        'pdf_search_flow': pdf_search_flow,
        'read_data_agent_flow': read_data_agent_flow,
        'schema_analyze_flow': schema_analyze_flow,
        'query_generator_flow': query_generator_flow,
        'query_executor_flow': query_executor_flow
    }

    @start()
    def specialist_selection(self):
        print(f"list of available specialists: {self.available_specialists.keys()}")
        team = ', '.join(
            [repr(name) for name in self.available_specialists.keys()]
        )
        query = self.state.query
        chosen_specialists = manager(team, query)
        self.state.chosen_specialists = chosen_specialists

    @listen(specialist_selection)
    def agent_execution(self):
        opinions: List[str] = []
        for specialist in self.state.chosen_specialists:
            try:
                opinion = self.available_specialists[specialist](
                    self.state.query,
                    **{
                        "image_path": self.state.image_path,
                        "pdf_path": self.state.pdf_path,
                        "json_path": self.state.json_path,
                        "database_connection": self.state.database_connection,
                        "table": self.state.table,
                        "last_agent_output": opinions if opinions else None
                    }
                )
                opinions.append(f"{specialist} stated: {opinion}")
                self.state.opinions = opinions
            except Exception as e:
                print(f"\nError: '{specialist}' key is not available.\n"+str(e))
                continue

    @listen(agent_execution)
    def generate_client_response(self):
        opinions = '; '.join(self.state.opinions)
        print(f"opinions from all the agents: {opinions}")
        print(f"qeury from the customer: {self.state.query}")
        client_response = client_outcome_architect(self.state.query, opinions)
        self.state.response = client_response
        print(f" Print statement for client outcome architect: {client_response}")
        return client_response
    


if __name__ == '__main__':
    question = input("[🤖 Help Desk]: Hi! How can I help you today?\n")
    flow = CustomerServiceFlow()
    result = flow.kickoff(
        inputs = {
            # "query": "add 5 items of LG  Direct-Cool Single Door Refrigerator to the cart",
            "query": "Get the total amount for the bill number   c64dc64d8e6b-8fd8-4274-be63-dd67d04d",
        # "query": "Get the total amount for the bill number d2f015b8-0d7e-420d-83a9-15c1236103f4",
        "image_path": os.path.join(os.path.dirname(__file__), 'data', 'image.jpg'),
        "pdf_path": "",
        "json_path": os.path.join(os.path.dirname(__file__), 'data', 'cart_output.json'),
        "database_connection":"postgresql:postgres:54321//@localhost:5432/postgres",
        "table": "product_details"
        }
    )
    print(f"\n[🤖 Final Answer]:\n{result}")
    # result = result[-1].split("{")[1:]
    print(f"\n[🤖 Flow State]:\n{flow.state}\n")

# "Get the total amount for the bill number 
# d2f015b8-0d7e-420d-83a9-15c1236103f4"
# Generate bill number
# "Update bill status as pending for the bill number d2f015b8-0d7e-420d-83a9-15c1236103f4"
# "Generate bill number for the items in the cart",

    
