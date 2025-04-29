from langchain.prompts import PromptTemplate

primary_classifier_prompt = PromptTemplate.from_template(
    """based on the subject line of an email, classify whether it is in regards to a job application
    or not. output the classification as one of the following categories: {categories}. only output {categories}. Respond with EXACTLY one of the following categories: YES, NO, MAYBE. 
    Do not include quotation marks, periods, or any extra text.
    Simply output the category word by itself in all caps.
    Subject: {subject} """
)

secondary_classifier_prompt = PromptTemplate.from_template(
    """Based on the email body classify whether the email is in regards to a job application. only output {categories}.
    ALWAYS output NO if email is about job perferences
    ALWAYS output NO if email is about job recommendation 
     ALWAYS output NO if email is about job alerts any job suggestions. 
     Output No if the email is not regarding an applied job
     read the whole email before deciding. by default your answer should be No.
     email subject: {subject}
    email body: {message}. 
    """
)

job_info_extractor_prompt = PromptTemplate.from_template(
    """You are an expert email classifier designed to identify emails related to job applications.


    Based **only** on the email body and subject, extract the following information from the email:
    - Job Title (if no job title is mentioned, use open role)
    - Company Name
    - location (if no location is mentioned, use N/A)
    - Application Status (e.g., "applied", "rejected", "interview scheduled", etc.)

    email subject: {subject}
    email body: {message}
    return the extracted information in the following format:
    Job Title: <job title>
    Company Name: <company name>
    Location: <location>
    Application Status: <application status>
    If the email does not contain any of the above information, return "N/A" for that field.
    return as json format.
    if there are multiple job titles, companies or locations, return them all in json format but number the keys.
    but do not return any other information or additional text."""
)