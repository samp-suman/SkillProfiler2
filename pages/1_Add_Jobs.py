# app.py

import streamlit as st
from module_utils.db.job_db import JobDatabase  # <<< importing here

# Initialize database
db = JobDatabase()

# --- Streamlit UI ---
st.title("Recruiter Job Submission Portal")
st.write("Fill out the form below to submit a new job opening.")

with st.form("job_submission_form"):
    company_name = st.text_input("Company Name")
    job_location = st.text_input("Job Location")
    job_role = st.text_input("Job Role")
    job_description = st.text_area("Job Description", height=200)

    submitted = st.form_submit_button("Submit Job")

    if submitted:
        if not (company_name and job_location and job_role and job_description):
            st.error("Please fill in all fields!")
        else:
            job_data = {
                "Company Name": company_name,
                "Job Location": job_location,
                "Job Role": job_role,
                "Job Description": job_description
            }
            db.save_job(job_data)
            st.success("Job submitted successfully!")

            st.subheader("Submitted Job Details")
            st.json(job_data)

# Optional: Display all submitted jobs
st.markdown("---")
if st.checkbox("Show all submitted jobs"):
    jobs = db.load_jobs()
    st.subheader("All Jobs Submitted")
    st.write(jobs)
