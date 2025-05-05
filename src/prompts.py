from langchain.prompts import PromptTemplate

primary_classifier_prompt = PromptTemplate.from_template(
    """based on the subject line of an email, classify whether it is in regards to a job application
    or not. output the classification as one of the following categories: {categories}. only output {categories}. Respond with EXACTLY one of the following categories: YES, NO, MAYBE. 
    Do not include quotation marks, periods, or any extra text.
    Simply output the category word by itself in all caps.
    Subject: {subject} """
)

secondary_classifier_prompt = PromptTemplate.from_template(
    """You are an expert email classifier. Given a raw email body determine if it's directly related to a job application.

    Rules:
    - Output **YES** only if the email is a **response to a job application** (e.g.applied, rejection, interview, offer).
    - Output **NO** if it's about:
    - Job preferences
    - Job recommendations
    - Job alerts or suggestions
    - Any email not about a specific application



    Input:
    Body: {message} 
    Output: YES or NO"""
)

job_info_extractor_prompt = PromptTemplate.from_template(
    """You are an expert info extractor designed to extract job info from emails related to job applications.

    You will be given raw email subject and body which may be noisy. 
    Based **only** on the email body and subject, extract the following information from the email:
    - Job Title (if no job title is mentioned, use open role)
    - Company Name
    - location (if no location is mentioned, use N/A)
    - Application Status (e.g., "applied", "rejected", "interview scheduled", etc.)

    email subject: {subject}
    email body: {message}
    return the extracted information in the following format:
    <job_info>
    job_title: <job title>
    company_name: <company name>
    location: <location>
    application_status: <application status>
    </job_info>
    If the email does not contain any of the above information, return "N/A" for that field. do not numbers or bullet points.

    
    """
)

data_cleaner_prompt = PromptTemplate.from_template(
    """You are an expert data cleaner. Given raw unprocessed email body which may be noisy, 
    and contain headers, footers, disclaimers, and other irrelevant information,
    clean and extract the email message by removing all the irrelevant information.
    Do not include any extra text or explanation. If the message maybe related to a job application,
    do not remove anything that may look like - the job title, company name, location and application status in the cleaned email body.
    email body: {message}
    return the cleaned email body.
    If the email body does not contain any relevant information, return "N/A".
    
    """
)