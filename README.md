# soft-engg-project-sep-2024-se-sep-5

## Prerequisites

Before running the application, ensure that the following prerequisites are met:

1. **Node.js**: Install the latest version of Node.js from [here](https://nodejs.org/).
2. **Python**: Install Python from [here](https://www.python.org/).

## How to Run the Application

Follow these steps to get the application up and running:

### Step 1: Clone the Repository
Copy the repository to your local machine and navigate to the `Code` folder:

```bash
cd Code
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

#### Store Tokens in `secret.sh`
Create a `secret.sh` file in the root of the project and add the following environment variables:

```bash
# In secret.sh file
export GITHUB_ACCESS_TOKEN="your_github_access_token_here"
export AI_ACCESS_TOKEN="your_ai_access_token_here"
```

Replace the values of `your_github_access_token_here` and `your_ai_access_token_here` with your actual tokens. After creating the file, run the following command to source it:

```bash
source secret.sh
```

### Step 3: Start the Backend Server
In the first terminal, navigate to the backend directory, install the necessary Python dependencies, and run the Flask application:

```bash
cd back-end
pip install -r requirements.txt
python main.py
```

### Step 4: Start the Frontend Development Server
In the second terminal, navigate to the frontend directory, install the necessary npm packages, and start the development server:

```bash
cd front-end
npm install
npm run dev
```

### Step 5: Access the Application
Open a web browser and navigate to the following URL to access the application:

```
http://localhost:5173/
```

### Step 6: Log In to the Application
Use the following credentials to log in as different users:

#### Instructor:
- **Username**: `profsmith`
- **Password**: `password123`

#### Teaching Assistant (TA):
- **Username**: `tajones`
- **Password**: `password123`

#### Student:
- **Username**: `student1`
- **Password**: `password123`