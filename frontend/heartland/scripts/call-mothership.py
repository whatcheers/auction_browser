import os
import json
from tqdm import tqdm
from openai import OpenAI

def get_openai_client():
    print("Attempting to retrieve OpenAI API key...")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        exit(1)
    else:
        print("OpenAI API key retrieved successfully.")
    return OpenAI(api_key=api_key)

def ask_gpt_with_json_file(file_path, instructions, client, model="gpt-4-1106-preview"):
    print(f"Loading JSON file from path: {file_path}")
    # Read and load the JSON file content
    with open(file_path, 'r') as file:
        file_content_json = json.load(file)
    
    print("JSON file loaded successfully.")
    # Convert the JSON object to a string representation
    file_content_str = json.dumps(file_content_json, indent=2)
    
    # Combine the instructions with the file content string
    combined_input = instructions + "\n\n" + file_content_str
    
    print("Sending request to OpenAI...")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": combined_input}
            ]
        )
        print("Request successful, response received.")
        # Accessing the content of the response
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred during request to OpenAI: {e}")
        return None

def main():
    file_path = "heartland-import.json" # Hardcoded file path
    instructions = ("Initial examination of the file revealed it contained structured JSON data describing auction items.\n"
                    "Extracted attributes for a selection of items, excluding location and pricing details, to provide valuable insights.\n"
                    "Report Generation:\n\n"
                    "compute the total number of items and categories present in the data file.\n"
                    "Collate information detailing the number of items per category for an overview of the auction inventory spread.\n"
                    #"For each category, we identified high-level information pertinent to asset managers, such as common brands and types of equipment.\n"
                    "Summary Response for Template:\n\n"
                    "Presented a concise report enumerating the aggregate data including the total number of items, the variety of categories, and the count of items in each category.\n"
                    #"Detailed a breakdown for each category highlighting top manufacturers which could inform the asset value and bidding strategy.\n"
		    "We do not need an explanation of what youre doing we just need a summary to report to managers at a high level.  A simple table is fine.\n"
		    "Most importantly the response should be generated as basic HTML Code.\n") 

    print("Initializing OpenAI client...")
    client = get_openai_client()
    
    # Initialize tqdm for progress tracking
    total_steps = 3  # Upload JSON file, send request, save response
    with tqdm(total=total_steps, desc="Processing") as pbar:
        # Upload and process JSON file
        pbar.set_description("Uploading JSON file")
        file_content_json = None
        with open(file_path, 'r') as file:
            file_content_json = json.load(file)
        pbar.update(1)
        
        # Process JSON content and send request to OpenAI
        pbar.set_description("Sending request to OpenAI")
        file_content_str = json.dumps(file_content_json, indent=2)
        combined_input = instructions + "\n\n" + file_content_str
        response = ask_gpt_with_json_file(file_path, instructions, client)
        pbar.update(1)
        
        # Save response as HTML
        pbar.set_description("Saving response")
        output_file_path = "../response.html"  # Save to parent directory
        with open(output_file_path, 'w') as file:
            file.write(response)
        pbar.update(1)
    
    print(f"Response successfully saved to {output_file_path}.")

if __name__ == "__main__":
    main()
