import sys
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # Load the environment variables from .env file

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_html.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]  # Filename from command line
    model = os.getenv('MODEL', 'gpt-4o')  # Use the model from .env, default to 'gpt-4o'
    num_completions = int(os.getenv('NUM_COMPLETIONS', 1))  # Get the number of completions from .env
    temperature = float(os.getenv('TEMPERATURE', 0.1))  # Get the temperature from .env

    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))  # Ensure you use the API key from .env

    with open(filename, "r") as file:
        html_content = file.read(250000)  # Read a substantial portion of the HTML file

    # Structured response setup in system's prompt
    system_prompt = (
        "You are a sophisticated AI trained to analyze HTML content of auction pages and extract detailed "
        "information in a structured format. Below is the HTML content you need to analyze. Provide the response "
        "in a structured summary including Title, Auction Type, Start and End Dates, Location, and Total Items."
    )

    # Hardcoded user query
    user_query = "Tell me about this auction"

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": html_content},
            {"role": "user", "content": user_query}
        ],
        max_tokens=200,
        n=num_completions,
        stop=None,
        temperature=temperature,
    )

    result = response.choices[0].message.content.strip()
    print(result)

    # Extract timestamp from the input HTML filename
    timestamp = filename.split('/')[-1].replace('.html', '')

    # Save the result to a file with the corresponding timestamp
    output_filename = f"output/output-{timestamp}.txt"
    with open(output_filename, "w") as output_file:
        output_file.write(result)
    print(f"Result has been saved to {output_filename}")

if __name__ == "__main__":
    main()
