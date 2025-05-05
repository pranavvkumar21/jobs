#!/usr/bin/env python3
import os
from langchain.chat_models import ChatOpenAI
from src.prompts import primary_classifier_prompt, secondary_classifier_prompt, job_info_extractor_prompt, data_cleaner_prompt
from langchain.chains import LLMChain
from tqdm import tqdm
import json,re

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
    def data_cleaner_agent(self, emails):
        # Define the prompt template
        prompt_template = data_cleaner_prompt
        for email in tqdm(emails, desc="running data cleaner agent"):
            #print(email)
            subject = email['subject']
            if email['primary_classification'] == "NO":
                continue
            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            # Run the chain
            result = chain.run(message=email['body'])

            email['cleaned_body'] = result
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
            #print('secondary classification:',email['secondary_classification'])
        return emails
    
    #agent to extract job info from the email
    def job_info_extractor_agent(self, emails):
        # Define the prompt template
        prompt_template = job_info_extractor_prompt
        for email in tqdm(emails, desc="running job info extractor agent"):
            #print(email)
            
            primary_classification = email['primary_classification']
            secondary_classification = email['secondary_classification']
            if primary_classification == "NO" or secondary_classification == "NO":
                continue
            # Create the LLM chain
            message = email['cleaned_body']
            subject = email['subject']
            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            # Run the chain
            result = chain.run(message=message,subject=subject)
            #result = response['text']
            # extract the job info from the result
            job_info = result.split("<job_info>")[1].split("</job_info>")[0]
            try:
                match = re.search(r"<job_info>(.*?)</job_info>", result, re.DOTALL)
                extracted = match.group(1) if match else None
                if extracted:
                    details = extracted.split("\n")
                    formatted_result = {}
                    for detail in details:
                        if ":" in detail:
                            key, value = detail.split(":", 1)
                            formatted_result[key.strip()] = value.strip()
                    #formatted_result = {k.strip(): v.strip() for k, v in (item.split(":", 1) for item in details)}
            except Exception as e:
                print(f"Error extracting job info: {e}")
                print(details)

            try:

                email['job_info'] = formatted_result
            except Exception as e:
                print(f"Error processing email: {email['subject']}")
                print(f"Error: {e}")
                # Handle the case where the result is not valid JSON

                continue
            #json_result = json.loads(result)
            
        return emails

    def run(self, emails):
        # Run the primary classifier agent
        emails = self.primary_classifier_agent(emails)
        # Run the data cleaner agent
        emails = self.data_cleaner_agent(emails)
        # Run the secondary classifier agent
        emails = self.secondary_classifier_agent(emails)
        # Run the job info extractor agent
        emails = self.job_info_extractor_agent(emails)
        return emails