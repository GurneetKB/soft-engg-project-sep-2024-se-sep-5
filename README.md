# soft-engg-project-sep-2024-se-sep-5
Here's the updated `README.md` with the `secret.sh` file and environment variable setup instructions added:

---

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

Create a `secret.sh` file in the root of the project and add the following environment variables:

```bash
# In secret.sh file
export GITHUB_ACCESS_TOKEN="your_github_access_token_here"
export AI_ACCESS_TOKEN="your_ai_access_token_here"
```

Make sure to replace the values of `your_github_access_token_here` and `your_ai_access_token_here` with your actual tokens. After creating the file, run the following command to source it:

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