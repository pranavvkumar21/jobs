# J.O.B.S — Job Opportunity Bot System

---

## 🛠️ Overview

**J.O.B.S** is a system designed to automate the process of:
- Fetching and parsing job-related emails
- Cleaning email bodies for consistent processing
- Classifying which emails are relevant to job applications
- Extracting structured job information (company name, role, application status)

The goal is to make job application tracking more reliable and less manual.

---

## Completed Tasks

- **Built base project framework**
- **Created configuration system**
- **Implemented EmailHandler class for fetching and parsing emails**
- **Developed email body cleaner for classification prep**
- **Created agent for classifying job-related emails**
- **Created agent for extracting job opportunity information**
- **Created a much better cleaning logic**
- **Implement spreadsheet insertion function**
---

## Upcoming Tasks

- **Secondary Classification Propmpt needs tweeking**
- **Experiment with agent to further clean data before passing to secondary classifier**
- **Add fuzzy search for matching similar company names and job titles**
- **Implement row update function for existing spreadsheet entries**

---

## Future Improvements (optional)

- Auto-detect and handle ghosted applications
- Track application stages (applied, interview, offer, rejected)
- Expand support for more job platforms (Indeed, Glassdoor, Wellfound)

---

## ⚡ Project Notes

- **Focus:** Start with LinkedIn emails first (most common and most inconsistent)
- **Gmail API Mode:** Testing `format=full` instead of `raw` to avoid unnecessary manual decoding
- **Parser Design:** Sender-based cleaning to handle differences across platforms
- **Goal:** Keep processing efficient, avoid wasting tokens or resources unnecessarily

---

## Known Challenges

- LinkedIn emails are inconsistently formatted and contain a lot of tracking artifacts
- Some recruiters use customized templates that may require special handling
- Email bodies often contain embedded noise even after initial decoding

---

# Current Phase:

**LinkedIn-only** cleanup and parsing focus, building a scalable structure to later support multiple job sources. 
**Creation and updation of job spreadsheet on gdrive**

