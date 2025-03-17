from crewai.tools import BaseTool
from google import genai
from googleapiclient.discovery import build
import os, requests
import PIL.Image
from dotenv import load_dotenv

dotenv_path = os.path.join(r'C:\Users\saahil.ali\OneDrive - Accenture\KT Documents\crewAI\product_inventory\.env')
load_dotenv(dotenv_path=dotenv_path)

api_key = os.getenv("GOOGLEKEY")
cse_id = os.getenv("CSEID")

class SearchWebTool(BaseTool):
    name: str = "Internet Search"
    description: str = "Useful for Internet search-based queries. Use this to find price of a product based on a model, brand, etc."

    def _run(self, query: str) -> str:
        try:
            service = build("customsearch", "v1", developerKey=api_key)
            result = service.cse().list(q=query, cx=cse_id).execute()
            return result
        except Exception as e:
            raise Exception(f"An error occurred: {e}")

class ShoppingAPITool(BaseTool):
    name: str = "Shopping API Tool"
    description: str = "A tool for making API calls to get details of product list, shopping cart or billing amount"

    def _run(self, endpoint: str, method: str = "GET", body: dict = None): 
        """Execute the API call and return results"""
        base_url = "http://127.0.0.1:8000/"
        api_endpoint = base_url + endpoint
        try:
            response = requests.request(method, api_endpoint, json=body)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return f"Error making API call: {str(e)}"

class SearchImageTool(BaseTool):
    name: str = "Image Search"
    description: str = "Useful for search context based on the Iamge given as input"

    def _run(self, prompt: str, image_path: str):
        # Implementation goes here
        try:
            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            image = PIL.Image.open(image_path)
            response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=[prompt, image])
            return response.text
        except Exception as e:
            raise Exception(f"An error occurred: {e}")