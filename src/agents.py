#!/usr/bin/env python3
import os
from langchain.chat_models import ChatOpenAI
from src.prompts import primary_classifier_prompt, secondary_classifier_prompt, job_info_extractor_prompt
from langchain.chains import LLMChain
from tqdm import tqdm
import json

class Agent:
    def __init__(self, openai_api_key):
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model="gpt-3.5-turbo",
            temperature=0)
    
    def primary_classifier_agent(self, emails):
        # Define the prompt template
        categories = ["YES, NO, MAYBE"]
        prompt_template = primary_classifier_prompt
        for email in tqdm(emails,desc="running primary classifier agent"):
            #print(email)
            subject = email['subject']
            #prompt = prompt_template.format(categories=categories, subject=subject)
            # Create the LLM chain
            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            # Run the chain
            result = chain.run(categories=categories, subject=subject)
            #print(f"Subject: {subject} \tClassification: {result}")
            email['primary_classification'] = result
        
        return emails
    def secondary_classifier_agent(self, emails):
        # Define the prompt template
        categories = ["YES, NO"]
        prompt_template = secondary_classifier_prompt
        for email in tqdm(emails, desc="running secondary classifier agent"):
            #print(email)
            message = email['body']
            subject = email['subject']
            primary_classification = email['primary_classification']
            if primary_classification == "NO":
                email['secondary_classification'] = "NO"
                continue
            
            # Create the LLM chain
            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            # Run the chain
            result = chain.run(message=message,subject=subject)
            #print(f"Subject: {subject} \t primary Classification: {primary_classification} \n secondary Classification: {result}")
            email['secondary_classification'] = result
            print('secondary classification:',email['secondary_classification'])
        return emails
    
    #agent to extract job info from the email
    def job_info_extractor_agent(self, emails):
        # Define the prompt template
        prompt_template = job_info_extractor_prompt
        for email in tqdm(emails, desc="running job info extractor agent"):
            #print(email)
            message = email['body']
            subject = email['subject']
            primary_classification = email['primary_classification']
            secondary_classification = email['secondary_classification']
            if primary_classification == "NO" or secondary_classification == "NO":
                continue
            # Create the LLM chain
            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            # Run the chain
            result = chain.run(message=message,subject=subject)
            try:
                # Convert the result to a dictionary
                json_result = json.loads(result)
                email['job_info'] = json_result
            except json.JSONDecodeError:
                # Handle the case where the result is not valid JSON
                print(f"Error decoding JSON: {result}. will be saved as is.")
                print(result)
                email['job_info'] = result
                # You can choose to skip this email or handle it differently
                continue
            #json_result = json.loads(result)
            
        return emails
