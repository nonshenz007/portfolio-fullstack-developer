import sys
import os
import yaml

# Add Core directory to path to import siblings
sys.path.append(os.path.dirname(__file__))
# from utils import llama_runner
# from memory import manage_db

def load_policy():
    """Loads the routing policy from the YAML file."""
    policy_path = os.path.join(os.path.dirname(__file__), 'policies', 'CLARA_POLICY.yaml')
    try:
        with open(policy_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"ERROR: Policy file not found at {policy_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"ERROR: Could not parse YAML policy file: {e}")
        sys.exit(1)

def get_intent(command, policy):
    """Determines the user's intent based on keywords in the policy."""
    command_lower = command.lower()
    for intent, config in policy['routing'].items():
        for keyword in config['keywords']:
            if keyword in command_lower:
                return intent, config
    return None, None

def print_help():
    """Prints the available commands."""
    print("\nAvailable Commands:")
    print("  predict <subject> - Analyze materials for likely exam topics.")
    print("  schedule          - Generate a study schedule.")
    print("  organize          - Create outlines, summaries, or flashcards from materials.")
    print("  help              - Show this help message.")
    print("  exit / quit       - Exit the application.")
    print()

def main_repl(policy):
    """The main Read-Eval-Print Loop for Clara."""
    print("Clara is ready. Type 'help' for a list of commands.")
    
    while True:
        try:
            prompt = input("Clara> ").strip()
            if not prompt:
                continue
            
            if prompt.lower() in ['exit', 'quit']:
                print("Exiting Clara. Happy studying!")
                break
            
            if prompt.lower() == 'help':
                print_help()
                continue

            intent, config = get_intent(prompt, policy)
            
            if intent:
                print(f"INTENT: {intent}")
                print(f"MODEL: {config['model']}")
                print(f"PROMPT: \n---\n{config['system_prompt']}\n---")
                # Here you would call the llama_runner with the prompt, model, etc.
                # e.g., llama_runner.invoke(model=config['model'], system_prompt=config['system_prompt'], user_command=prompt)
                print("\n(Simulation: Llama.cpp would be invoked here)\n")
            else:
                print("Sorry, I don't understand that command. Type 'help' for options.")

        except KeyboardInterrupt:
            print("\nExiting Clara. Happy studying!")
            break
        except EOFError:
            print("\nExiting Clara. Happy studying!")
            break

if __name__ == "__main__":
    policy = load_policy()
    main_repl(policy)
