#!/usr/bin/env python3
"""
Example for Tip 038: Attribute-First Data Generation

This example demonstrates how to generate diverse synthetic data by creating
attributes first, then generating data based on those attributes.
"""

from mirascope import llm, prompt_template
from pydantic import BaseModel
from typing import Literal

class CustomerProfile(BaseModel):
    user_type: Literal["new_customer", "long_term_customer", "enterprise_user", "free_tier_user"]
    technical_expertise: Literal["beginner", "intermediate", "expert"]
    urgency_level: Literal["low", "medium", "high", "critical"]
    communication_style: Literal["formal", "casual", "frustrated", "polite"]

@llm.call(provider='openai', model='gpt-4o-mini', response_model=CustomerProfile)
@prompt_template("Generate a diverse customer profile for a billing support scenario. Vary the attributes to create different types of customers.")
def generate_customer_profile(): ...

@llm.call(provider='openai', model='gpt-4o-mini')
@prompt_template("""
Generate a realistic customer support conversation about billing issues with this customer profile:
- User type: {profile.user_type}
- Technical expertise: {profile.technical_expertise}  
- Urgency level: {profile.urgency_level}
- Communication style: {profile.communication_style}

Make sure the conversation reflects these specific attributes. Include both customer and support agent messages.
Keep it realistic and under 500 words.
""")
def generate_conversation_for_profile(profile: CustomerProfile): ...

def main():
    print("=== Attribute-First Data Generation Example ===\n")
    
    # Generate diverse profiles first
    print("Step 1: Generating diverse customer profiles...")
    profiles = []
    for i in range(3):
        profile = generate_customer_profile()
        profiles.append(profile)
        print(f"Profile {i+1}: {profile.model_dump()}")
    
    print("\nStep 2: Generating conversations based on profiles...")
    
    # Generate conversations based on the profiles
    for i, profile in enumerate(profiles):
        print(f"\n--- Conversation {i+1} ---")
        print(f"Profile: {profile.user_type}, {profile.technical_expertise}, {profile.urgency_level}, {profile.communication_style}")
        print("Conversation:")
        conversation = generate_conversation_for_profile(profile)
        print(conversation)
        print("-" * 50)

if __name__ == "__main__":
    main()