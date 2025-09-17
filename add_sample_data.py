# add_sample_data.py

from database0 import internship_collection

# Clear existing data to avoid duplicates if you re-run the script
internship_collection.delete_many({})

sample_internships = [
    {"title": "Backend Developer Intern", "company": "Tech Solutions Inc.", "location": "Remote", "stipend": 25000, "required_skills": ["Python", "FastAPI", "MongoDB", "REST APIs"]},
    {"title": "Frontend Developer Intern", "company": "Creative Minds", "location": "New York", "stipend": 20000, "required_skills": ["JavaScript", "React", "HTML", "CSS"]},
    {"title": "Data Science Intern", "company": "Data Insights LLC", "location": "Remote", "stipend": 30000, "required_skills": ["Python", "Pandas", "NumPy", "SQL"]},
    {"title": "Cloud Engineering Intern", "company": "InfraCloud", "location": "San Francisco", "stipend": 35000, "required_skills": ["AWS", "Docker", "Python"]},
    {"title": "Mobile App Development Intern", "company": "Appify", "location": "Remote", "stipend": 22000, "required_skills": ["Flutter", "Dart", "Firebase"]},
    {"title": "Full Stack Developer Intern", "company": "Innovatech", "location": "Austin", "stipend": 28000, "required_skills": ["React", "Node.js", "MongoDB"]},
    {"title": "Data Analyst Intern", "company": "NumberCrunchers", "location": "Remote", "stipend": 18000, "required_skills": ["SQL", "Excel", "Tableau", "Python"]}
]

try:
    result = internship_collection.insert_many(sample_internships)
    print(f"Successfully inserted {len(result.inserted_ids)} internships into the local database.")
except Exception as e:
    print(f"An error occurred: {e}")