#!/usr/bin/env python3
import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from tqdm import tqdm

class Agent:
    def __init__(self, openai_api_key):
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model="gpt-3.5-turbo",
            temperature=0)
    
    def primary_classifier_agent(self, emails):
        # Define the prompt template
        categories = ["YES, NO, MAYBE"]
        prompt_template = PromptTemplate.from_template(
            """based on the subject line of an email, classify whether it is in regards to a job application
            or not. output the classification as one of the following categories: {categories}.
            Subject: {subject} """
        )
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
        prompt_template = PromptTemplate.from_template(
            """You are an expert email classifier designed to identify emails related to job applications.

            Based **only** on the email body and subject, determine whether the email is about a specific job application that the recipient has submitted or is being considered for.
            This includes emails that confirm the application was received, even if the employer has not yet made a decision.

            Exclude the following types of emails:
            - General job opportunity alerts or newsletters
            - Feedback requests
            - Surveys
            - Career platform engagement emails (e.g., "new jobs for you", "update your profile")
            - Emails that are not related to job applications

            Classify the email into one of the following categories: {categories} 

            Email Content:
            {message}"""
        )
        for email in tqdm(emails, desc="running secondary classifier agent"):
            #print(email)
            message = email['body']
            subject = email['subject']
            primary_classification = email['primary_classification']
            if primary_classification == "NO":
                continue
            
            # Create the LLM chain
            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            # Run the chain
            result = chain.run(categories=categories, message=message)
            #print(f"Subject: {subject} \t primary Classification: {primary_classification} \n secondary Classification: {result}")
            email['secondary_classification'] = result
        
        return emails
