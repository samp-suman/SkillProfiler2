import streamlit as st
import google.generativeai as genai
import google.api_core.exceptions

import os
import dotenv
import json
import PyPDF2

# Load environment variables
if os.path.exists("db/jobs.json"):
    with open("db/jobs.json", "r") as f:
        job_dict = json.load(f)
else:
    job_dict = {}
   
model = None



def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF."""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    return text


def extract_skills_from_resume(resume_text):
    """Extract technical and soft skills from resume text using Gemini API."""
    prompt = f"Extract technical and soft skills from the following resume text:\n{resume_text}\nReturn the skills as a comma-separated list."

    try:
        response = model.generate_content(prompt)
        return response.text.strip() if response and response.text else "No skills extracted."
    except google.api_core.exceptions.ResourceExhausted as e:
        st.error("You have exceeded your API quota. Please check your billing and plan details.")
        return "Error: API quota exceeded"
    except Exception as e:
        st.error(f"An error occurred while extracting skills: {str(e)}")
        return "Error in skill extraction"



def generate_questions(skills, selected_job):
    """Generate interview questions based on extracted skills using Gemini API."""
    prompt = f"Generate 5 interview questions based on these skills: {skills}. \
        ## Job Description : {job_dict[selected_job]['Job Description']}\n \
        # Return them as a numbered list. Just start giving questions, not the text like Here are five questions and other such texts."

    try:
        response = model.generate_content(prompt)
        return [q.strip() for q in response.text.split("\n") if q.strip()] if response and response.text else []
    except google.api_core.exceptions.ResourceExhausted as e:
        st.error("You have exceeded your API quota. Please check your billing and plan details.")
        return []  # Return an empty list if quota exceeded
    except Exception as e:
        st.error(f"An error occurred while generating questions: {str(e)}")
        return []  # Return empty list if any other exception occurs

def evaluate_answers(questions, answers, selected_job):
    """Evaluate user answers using Gemini API."""
    results = {}

    for idx, (q, ans) in enumerate(zip(questions, answers)):
        if not ans.strip():
            results[q] = {"answer": ans, "score": "0"}
            continue

        prompt = f"Evaluate the following answer Keeping in mind of the ##Job Description: {job_dict[selected_job]['Job Description']} \n \
                ##Question: '{q}'\n \
                ##Answer: {ans}\nProvide a score (0-10) I just want a integer response - 0-10, no extra text, no feedback, just marks out of 10."
        
        try:
            response = model.generate_content(prompt)

            if response and response.text:
                results[q] = {"answer": ans, "score": response.text.strip()}
            else:
                results[q] = {"answer": ans, "score": "Error in evaluation"}
        except google.api_core.exceptions.ResourceExhausted as e:
            st.error("You have exceeded your API quota. Please check your billing and plan details.")
            break  # You can break or return here based on how you want to handle the failure.
        except Exception as e:
            st.error(f"An error occurred while evaluating the answer: {str(e)}")
            results[q] = {"answer": ans, "score": "Error in evaluation"}

    return results


def save_to_json(data, filename="db/exam_results.json"):
    """Save the exam results to a JSON file."""
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def get_job_listing(job_id):
    job_data = job_dict.get(job_id)
    print(job_data)
    job_titles = f"{job_data['Job Role']} at {job_data['Company Name']} ({job_data['Job Location']})"
    return job_titles


def main():
    global model
    """Streamlit UI for Job Application and Skill Evaluation."""
    st.title("Apply for a Job Opening 🚀")
    if not job_dict:
        st.warning("No job openings available at the moment. Please check back later.")
        return
    if 'gemini_api_key' not in st.session_state or st.session_state.gemini_api_key is None:
        st.warning("Please set your Gemini API Key before proceeding.")
        # Redirect the user to the main page to input the API key
        st.markdown('<a href="/" target="_self">Click here to go back to Home page</a>', unsafe_allow_html=True)
        return
    api_key = st.session_state.gemini_api_key
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    # Select a Job
    st.subheader("Select a Job to Apply")
    
    selected_job = st.selectbox("Choose a Job Opening", job_dict.keys(), format_func=get_job_listing)

    if selected_job:
        st.success(f"You have selected: **{selected_job}**")
        st.json(job_dict[selected_job])

        st.subheader("Apply for the Job Opening")
        # Initialize session state variables
        if "skills" not in st.session_state:
            st.session_state.skills = None
        if "questions" not in st.session_state:
            st.session_state.questions = None
        if "answers" not in st.session_state:
            st.session_state.answers = []

        uploaded_file = st.file_uploader("📄 Upload your resume (PDF)", type=["pdf"])

        if uploaded_file:
            resume_text = extract_text_from_pdf(uploaded_file)
            
            if resume_text and st.button("🔍 Extract Skills"):
                st.session_state.skills = extract_skills_from_resume(resume_text)
            
            if st.session_state.skills:
                st.success(f"**Extracted Skills:** {st.session_state.skills}")

                if st.button("🎯 Generate Questions"):
                    st.session_state.questions = generate_questions(st.session_state.skills, selected_job)
                    st.session_state.answers = [""] * len(st.session_state.questions)  # Reset answers
            
            if st.session_state.questions:
                st.subheader("Answer the following questions:")
                for i, q in enumerate(st.session_state.questions):
                    st.session_state.answers[i] = st.text_area(f"📝 {q}", value=st.session_state.answers[i], key=f"answer_{i}")

                if st.button("✅ Submit Exam"):
                    st.subheader("Evaluating Answers...")
                    results = evaluate_answers(st.session_state.questions, st.session_state.answers, selected_job)

                    # Calculate Total Score
                    total_score = sum(
                        int(v["score"].split()[0]) for v in results.values() if v["score"].split()[0].isdigit()
                    )

                    st.success(f"🎯 **Total Score: {total_score}/50**")
                    
                    # Save exam results with job applied info
                    application_data = {
                        "Selected Job": selected_job,
                        "Results": results,
                        "Total Score": total_score
                    }
                    save_to_json(application_data)  # You might adjust filename or db saving here
                    st.write("📂 **Application and Exam results saved successfully!**")

                    # Display Results
                    st.subheader("Detailed Results:")
                    for q, result in results.items():
                        st.write(f"**Q:** {q}")
                        st.write(f"**Your Answer:** {result['answer']}")
                        st.write(f"**Score & Feedback:** {result['score']}")
                        st.markdown("---")


if __name__ == "__main__":
    main()
