GRC Risk Assessment & Heatmap Dashboard

This project is a small full-stack application built to assess, store, and visualize risks using a standard Likelihood × Impact risk matrix. It simulates a core feature commonly found in real-world GRC (Governance, Risk, and Compliance) tools used for security and operational risk assessments.

The backend is implemented using FastAPI, and the frontend dashboard is built with Streamlit, following the technology stack specified in the assignment.

How the Application Works (GRC Logic)

The application follows the commonly used risk assessment approach aligned with frameworks such as NIST SP 800-30.

Risk Scoring
Each risk is scored using the formula:
Risk Score = Likelihood × Impact
where both Likelihood and Impact range from 1 to 5.

Risk Levels

1–5 → Low

6–12 → Medium

13–18 → High

19–25 → Critical

Heatmap Visualization
A 5×5 risk matrix displays how risks are distributed across likelihood and impact values. Each cell is color-coded based on the severity of the calculated risk score.

Mitigation Guidance
Simple mitigation suggestions are shown based on the risk level to reflect realistic GRC decision-making.

Core Features

Risk Assessment Form

Asset and threat input fields

Sliders for likelihood and impact (1–5)

Real-time preview of risk score and level before submission

Dashboard

Risk Heatmap: Color-coded 5×5 matrix with hover details

Risk Register: Sortable and filterable table of all assessed risks

Summary Metrics: Total risks, high/critical risks, and average risk score

Persistence

All risk data is stored locally using SQLite (risks.db)

Export

Risk register can be downloaded as a CSV file for reporting or offline analysis

Setup Instructions
1. Install Dependencies
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt

2. Run the Application

Start Backend

cd backend
python -m uvicorn app:app --reload


Start Frontend

cd frontend
streamlit run app.py

Challenges Faced During Development

Keeping frontend and backend logic consistent
One of the main challenges was ensuring that the real-time risk preview in the frontend always matched the backend’s calculation and classification logic. This required careful handling of boundary cases (for example, score transitions between Medium and High).

Heatmap implementation
Building the 5×5 risk matrix was more complex than expected. Initially, the focus was only on showing counts, but later it became clear that the color of each cell needed to reflect the risk severity derived from likelihood × impact, not just frequency. This was addressed by mapping score ranges directly to color bands.

Handling empty and refresh states
When no risks were present or when new risks were added, the dashboard needed to handle these transitions cleanly. Explicit empty states and careful use of Streamlit caching were added to avoid confusing UI behavior.

Technology choice trade-offs
Although React was an option, Streamlit was chosen to prioritize correctness, data visualization, and faster iteration within the given time constraints.

Recent Updates 

Updated the frontend to use the deployed backend API instead of localhost to support cloud deployment.
Improved frontend error handling to gracefully handle backend connectivity issues.
For running the frontend locally, the backend API is configured as:
API_URL = http://localhost:8000 
Make sure the FastAPI backend is running locally before starting the frontend.
Live Demo of Application (Frontend using Streamlit on Render):  
https://grc-filter-task-lavesh-karadia-frontend.onrender.com

Testing

Basic unit tests are included to validate the most critical part of the system: the risk classification and compliance logic.

Tests cover:

Risk level mapping across boundary values

Compliance hint behavior for high and critical risks

Handling of invalid risk scores

Run tests using:

cd backend
pytest

Core Skills & Primary Stack

Java & Spring Boot (Primary Expertise)
My core backend experience is in Java and Spring Boot, including REST API development, layered architecture, validation, database integration, and testing. The backend design in this project follows the same principles I apply in Spring Boot applications, even though FastAPI is used here.

Backend API Design
Experience designing clean, maintainable APIs with clear separation of concerns and well-defined business logic.

GRC & Risk Assessment Fundamentals
Practical understanding of likelihood-impact risk models used in governance and compliance contexts.

Relational Databases & Data Modeling
Comfortable working with SQL databases and designing schemas for structured data persistence.

Testing Mindset
Familiar with unit testing practices from Java (JUnit/Mockito) and applied the same principles here using pytest.

Note on Technology Choice

The technology stack used in this project strictly follows the assignment requirements. While my primary backend stack is Java + Spring Boot, the concepts demonstrated here—API design, validation, business logic separation, persistence, and testing—are directly transferable to a Spring Boot implementation.

Assumptions & Limitations

Single-user, local application

No authentication or role-based access control

SQLite used for simplicity and local storage

Risk thresholds and mitigation guidance are intentionally simplified

Designed as a demonstration of GRC risk assessment, not a production-ready GRC platform
