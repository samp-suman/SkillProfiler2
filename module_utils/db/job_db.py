import json
import os
import uuid

class JobDatabase:
    def __init__(self, file_path="db/jobs.json"):
        self.file_path = file_path
        
        # Check if file exists
        if not os.path.exists(self.file_path):
            # Create the file with an empty dictionary if it doesn't exist
            with open(self.file_path, "w") as f:
                json.dump({}, f)
        else:
            # If file exists, read it and check for content
            with open(self.file_path, "r") as f:
                content = f.read().strip()  # Read content and remove extra spaces or newlines
                if not content:  # If empty, write an empty dictionary
                    with open(self.file_path, "w") as f:
                        json.dump({}, f)

    def load_jobs(self):
        """Load jobs from the database."""
        with open(self.file_path, "r") as f:
            return json.load(f)

    def save_job(self, job_data):
        """Save a new job entry with a unique job_id as key."""
        jobs = self.load_jobs()

        # Generate a unique job ID
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        job_data["job_id"] = job_id  # Include the job_id in the job data

        # Add job to the jobs dictionary with job_id as key
        jobs[job_id] = job_data

        # Save updated jobs data to the file
        with open(self.file_path, "w") as f:
            json.dump(jobs, f, indent=4)

    def get_job(self, job_id):
        """Get a job by job_id."""
        jobs = self.load_jobs()
        return jobs.get(job_id)

    def update_job(self, job_id, job_data):
        """Update an existing job by job_id."""
        jobs = self.load_jobs()
        if job_id in jobs:
            jobs[job_id].update(job_data)
            with open(self.file_path, "w") as f:
                json.dump(jobs, f, indent=4)
            return True
        return False

    def delete_job(self, job_id):
        """Delete a job by job_id."""
        jobs = self.load_jobs()
        if job_id in jobs:
            del jobs[job_id]
            with open(self.file_path, "w") as f:
                json.dump(jobs, f, indent=4)
            return True
        return False
