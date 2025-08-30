
#!/usr/bin/env python3

import os
import argparse
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def main():
    """
    Example script demonstrating how to use LangChain with Claude 3.7 model
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='LangChain with Claude 3.7 example')
    parser.add_argument('--api-key', help='Anthropic API key')
    parser.add_argument('--demo', action='store_true', help='Run in demo mode without API calls')
    args = parser.parse_args()
    
    # Check for API key
    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY")
    
    # Demo mode for showing the script structure without making actual API calls
    demo_mode = args.demo
    
    if not api_key and not demo_mode:
        print("Warning: ANTHROPIC_API_KEY environment variable not set.")
        print("Please set your API key with: export ANTHROPIC_API_KEY='your_api_key'")
        print("Or run with --demo flag to see the script structure without making API calls.")
        print("For this example, you'll be prompted to enter your API key:")
        api_key = input("Enter your Anthropic API key (or type 'demo' for demo mode): ")
        if api_key.lower() == 'demo':
            demo_mode = True
            api_key = "dummy_api_key_for_demo"
        elif not api_key:
            print("No API key provided. Exiting.")
            return
        
    if api_key:
        os.environ["ANTHROPIC_API_KEY"] = api_key

    # Initialize the Claude 3.7 model
    print("Initializing Claude 3.7 model...")
    model = ChatAnthropic(model="claude-3-7-sonnet-20240620")
    
    # Create a prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant that provides concise and accurate information."),
        ("human", "{input}")
    ])
    
    # Create a simple chain: prompt -> model -> output parser
    chain = prompt | model | StrOutputParser()
    
    # Example usage
    print("\nExample 1: Basic question answering")
    print("---------------------------------")
    response = chain.invoke({"input": "What are the three laws of robotics?"})
    print(f"Response: {response}\n")
    
    print("\nExample 2: Code generation")
    print("---------------------------------")
    response = chain.invoke({"input": "Write a Python function to calculate the Fibonacci sequence up to n terms."})
    print(f"Response: {response}\n")
    
    # Interactive mode
    print("\nInteractive Mode")
    print("---------------------------------")
    print("Type your questions to Claude 3.7 (type 'exit' to quit)")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit", "q"]:
            break
            
        response = chain.invoke({"input": user_input})
        print(f"\nClaude: {response}")

if __name__ == "__main__":
    main()
