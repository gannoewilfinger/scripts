import os
import re
import logging
from datetime import datetime

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SecurityPolicyEnforcer:
    def __init__(self, policy_file='security_policies.txt'):
        self.policy_file = policy_file
        self.policies = self._load_policies()

    def _load_policies(self):
        policies = []
        if not os.path.exists(self.policy_file):
            logging.warning(f"Policy file {self.policy_file} not found. Using default policies.")
            return policies
        
        with open(self.policy_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    policies.append(line)
        return policies

    def _check_policy(self, content):
        for policy in self.policies:
            # Check for forbidden words or patterns
            if re.search(policy, content, re.IGNORECASE):
                logging.warning(f"Policy violation detected: {policy}")
                return False
        return True

    def enforce_policy(self, content):
        if not self._check_policy(content):
            raise ValueError("Security policy violation detected.")
        logging.info("Security policy check passed.")
        return content

if __name__ == "__main__":
    # Example usage
    enforcer = SecurityPolicyEnforcer()
    sample_content = "This is a test content with sensitive data like passwords and keys."
    try:
        sanitized_content = enforcer.enforce_policy(sample_content)
        print("Content is compliant with security policies.")
    except ValueError as e:
        print(f"Error: {e}")