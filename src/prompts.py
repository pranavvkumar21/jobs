from langchain.prompts import PromptTemplate

primary_classifier_prompt = PromptTemplate.from_template(
    """based on the subject line of an email, classify whether it is in regards to a job application
    or not. output the classification as one of the following categories: {categories}. only output {categories}. Respond with EXACTLY one of the following categories: YES, NO, MAYBE. 
    Do not include quotation marks, periods, or any extra text.
    Simply output the category word by itself in all caps.
    Subject: {subject} """
)

secondary_classifier_prompt = PromptTemplate.from_template(
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
    Do not include quotation marks, periods, or any extra text.
    Output should be in all caps.
    Email Content:
    {message}"""
)

job_info_extractor_prompt = PromptTemplate.from_template(
    """You are an expert email classifier designed to identify emails related to job applications.
    The email may contain noise such as:
    - Tracking tokens (e.g., "lipi urn", "midToken", "trkEmail")
    - Broken URLs
    - Help and Unsubscribe footer text
    - Random strings of characters and numbers.
    you should:
    - Focus ONLY on meaningful human-readable English sentences.
    - Ignore all lines or parts that look like broken links, tokens, or tracking parameters.

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