import json
import random
import string

class NoidMinter:
    def __init__(self, minter_state_path):
        """Initialize the NoidMinter with the path to the minter state JSON file."""
        self.minter_state_path = minter_state_path
        self.minter_state = self.load_minter_state(minter_state_path)

    def load_minter_state(self, filepath):
        """Load the minter state from the specified JSON file."""
        with open(filepath, 'r') as file:
            return json.load(file)

    def save_minter_state(self):
        """Save the current minter state back to the JSON file."""
        with open(self.minter_state_path, 'w') as file:
            json.dump(self.minter_state, file)

    def generate_noid(self, length=10):
        """Generate a new NOID using the current rand string and seq number."""
        rand_string = self.minter_state['rand']
        seq = self.minter_state['seq']
        counters = self.minter_state['counters']

        # Combine rand_string and seq to create a unique seed for randomness
        seed_value = f"{rand_string}{seq}"
        random.seed(seed_value)

        # Create a character pool (lowercase alphanumeric)
        characters = string.ascii_lowercase + string.digits

        # Generate a NOID of the specified length
        noid = ''.join(random.choice(characters) for _ in range(length))

        # Update the counter for the generated NOID (increment the first counter's value)
        counters[0]['value'] += 1  

        # Save the updated state back to the JSON file
        self.minter_state['seq'] += 1  # Increment seq for the next mint
        self.save_minter_state()  # Save changes

        return noid

    def mint(self):
        """Public method to mint a new NOID."""
        return self.generate_noid()

# If you want to run this as a script from the command line
if __name__ == '__main__':
    import sys
    # Check that a path to the minter state file was provided as an argument
    if len(sys.argv) != 2:
        print("Usage: python noid_minter.py <path_to_minter_state.json>")
        print("Example: python noid_minter.py ../minter_state.json")
        sys.exit(1)

    minter_state_path = sys.argv[1]
    noid_minter = NoidMinter(minter_state_path)  # Create an instance of NoidMinter
    noid = noid_minter.mint()  # Mint a new NOID
    print("Generated NOID:", noid)  # Output the generated NOID

# The NoidMinter can also be used as a library:
# from noid_minter import NoidMinter
# minter = NoidMinter('<path_to_minter_state.json>')
# new_noid = minter.mint()
# print(new_noid)
