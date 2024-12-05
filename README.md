# Tracky | The Project Tracking System

## Description

Tracky is a comprehensive project tracking system designed to streamline the management, tracking, and feedback processes for student projects in an educational setting. The system provides distinct functionalities for instructors, teaching assistants, and students, focusing on milestones, task submissions, and progress tracking. Advanced integrations with GitHub and Generative AI enhance the application's capabilities by automating analysis and offering actionable insights.

## Key Features

- **Milestone and Task Management**: Create, update, track, and delete milestones and associated tasks, ensuring timely delivery and progress tracking.
- **Submission Tracking and Feedback**: Allow students to submit work, with instructors and TAs providing detailed feedback on specific tasks.
- **GitHub Integration**: Monitor team and individual commit histories to evaluate contributions and development progress.
- **AI-Driven Insights**: Leverage AI for analyzing document submissions and team progress.
- **Role-Based Access Control**: Tailored access for instructors, TAs, and students to ensure security and relevant functionalities for each role.
- **Student AI Chat Assistant**: Assist students with milestone-related queries, focusing on operational and project management aspects.
- **Dashboard Analytics**: Provide instructors with comprehensive statistics on team progress, milestone completion, and individual performance.

## Technologies Used

| Category | Technology | Description |
|----------|------------|-------------|
| **Version Control & Project Management** |
| | GitHub | Version control, code management, issue tracking, and code review |
| | Jira | Agile project management and issue tracking |
| **Design & Prototyping** |
| | Figma | Collaborative interface design and prototyping |
| | Canva | Graphic design and visual content creation |
| | Mermaid (draw.io) | Diagramming and charting tool for visual documentation |
| **Frontend Development** |
| | Vue 3 | Progressive JavaScript framework for building user interfaces |
| | Vite | Next-generation frontend tooling for faster development |
| | Pinia | Intuitive, type-safe, and flexible Vue Store |
| | Vue Router | Official router for Vue.js applications |
| | Bootstrap | Responsive, mobile-first frontend framework |
| **Backend Development** |
| | Flask | Lightweight WSGI web application framework in Python |
| | Flask-Security-Too | Adds security features to Flask applications |
| | SQLAlchemy | SQL toolkit and Object-Relational Mapping (ORM) library |
| | SQLite | Self-contained, serverless, and zero-configuration database engine |
| | OpenAPI | Standard for RESTful API description |
| **Testing & Validation** |
| | Pytest | Testing framework for Python |
| | Vee-validate | Template-based validation framework for Vue.js |
| | Yup | JavaScript schema builder for value parsing and validation |
| **AI & Data Processing** |
| | Groq | AI infrastructure for running large language models |
| | Llama | Large language model for AI-driven functionalities |
| | Pydantic | Data validation and settings management using Python type annotations |
| **Integration & Utilities** |
| | PyGitHub | Python library to access the GitHub API |
| | jsPDF | Client-side JavaScript PDF generation |
| | Marked | Markdown parser and compiler for JavaScript |
| | sanitize-html | Library for sanitizing HTML and preventing XSS attacks |
| | PyPDF2 | Python library for reading PDF files |


## Prerequisites

Before running the application, ensure that the following prerequisites are met:

1. **Node.js**: Install the latest version of Node.js from [here](https://nodejs.org/).
2. **Python**: Install Python from [here](https://www.python.org/).

## How to Run the Application

Follow these steps to get the application up and running on your operating system:

### Step 1: Clone the Repository

For both macOS/Linux and Windows:

```bash
git clone https://github.com/GurneetKB/soft-engg-project-sep-2024-se-sep-5.git
cd soft-engg-project-sep-2024-se-sep-5
```

### Step 2: Set Up Environment Variables

#### GitHub Personal Access Token (Classic)

To enable GitHub API access, you'll need to create a **Personal Access Token (Classic)** with repository access. Follow these steps:

1. Go to [GitHub's Personal Access Token page](https://github.com/settings/tokens).
2. Click **Generate New Token**.
3. Select the required scopes, ensuring **repo** (for repository access) is enabled.
4. Click **Generate Token**.
5. Copy the generated token and use it in the following steps.


Make sure you are either the **owner** or a **collaborator** of the repository you want to access with the token. 

#### AI Token (Groq)

To use AI services, you'll need to create an **AI token** via Groq:

1. Sign up or log in to your Groq account at [Groq](https://console.groq.com/keys).
2. Create a new API key and copy it.


#### Store Tokens in Environment Variables

##### For macOS/Linux:

Create a `secret.sh` file in the root of the project and add the following environment variables:

```shellscript
# In secret.sh file
export GITHUB_ACCESS_TOKEN="your_github_access_token_here"
export AI_ACCESS_TOKEN="your_ai_access_token_here"
```

Replace the values with your actual tokens. After creating the file, run:

```shellscript
source secret.sh
```

##### For Windows:

Create a `secret.bat` file in the root of the project and add the following environment variables:

```plaintext
@echo off
set GITHUB_ACCESS_TOKEN=your_github_access_token_here
set AI_ACCESS_TOKEN=your_ai_access_token_here
```

Replace the values with your actual tokens. After creating the file, run:

```plaintext
secret.bat
```

### Step 3: Update GitHub Information

Before starting the backend server, you need to update the `initial_data.py` file with GitHub usernames and repositories that you want to access, if you want to fully use all the app's features.

1. Open the file `back-end/application/initial_data.py` in a text editor.
2. Locate the following sections and update them with your GitHub information:

```python
   github_username = ["your_username1", "your_username2", "your_username3"]
```

Replace `your_username1`, `your_username2`, and `your_username3` with GitHub usernames.

3. Update the `github_repo_url` for each team:

```python
Teams(
    name="Team Alpha",
    github_repo_url="https://github.com/your_username/team_alpha",
    # ... other fields ...
),
```

Replace the `github_repo_url` for each team with repositories you have access to.

4. Save the changes to the file.

### Step 4: Start the Backend Server

##### For macOS/Linux:

```shellscript
cd back-end
pip3 install -r requirements.txt
python3 main.py
```

##### For Windows:

```plaintext
cd back-end
pip install -r requirements.txt
python main.py
```

### Step 5: Start the Frontend Development Server

Open a new terminal window and navigate to the project root directory.

##### For both macOS/Linux and Windows:

```shellscript
cd front-end
npm install
npm run dev
```

### Step 6: Access the Application

Open a web browser and navigate to the following URL to access the application:

```plaintext
http://localhost:5173/
```

### Step 7: Log In to the Application

Use the following credentials to log in as different users:

#### Instructor:

- **Username**: profsmith
- **Password**: password123


#### Teaching Assistant (TA):

- **Username**: tajones
- **Password**: password123


#### Student:

- **Username**: student1
- **Password**: password123