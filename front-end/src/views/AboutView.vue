<script setup>
  import { ref } from 'vue'

  const teamRoles = ref( [
    { title: 'Scrum Master', description: 'Facilitates team operations and ensures smooth progress.' },
    { title: 'Project Manager', description: 'Manages tasks, deadlines, and resource allocation.' },
    { title: 'Backend Developer', description: 'Builds and manages server-side functionality.' },
    { title: 'Frontend Developer', description: 'Creates the user interface and experience.' },
    { title: 'Tester', description: 'Ensures quality and reliability through rigorous testing.' }
  ] )

  const technologyGroups = ref( [
    {
      title: 'Version Control & Project Management',
      technologies: [ 'GitHub', 'Jira' ]
    },
    {
      title: 'Design & UI',
      technologies: [ 'Figma', 'Canva', 'Mermaid (draw.io)' ]
    },
    {
      title: 'Frontend Development',
      technologies: [ 'Vue 3', 'Vite', 'Pinia', 'vue-router', 'Bootstrap' ]
    },
    {
      title: 'Backend Development',
      technologies: [ 'Flask', 'Flask-Security-Too', 'SQLAlchemy', 'SQLite', 'OpenAPI' ]
    },
    {
      title: 'Testing & Validation',
      technologies: [ 'Pytest', 'vee-validate', 'Yup', 'sanitize-html' ]
    },
    {
      title: 'AI & Data Processing',
      technologies: [ 'Groq', 'Llama', 'Pydantic' ]
    },
    {
      title: 'Integration & Utilities',
      technologies: [ 'PyGitHub', 'jsPDF', 'Marked', 'PyPDF2' ]
    }
  ] )
</script>

<template>
  <div class="about-page container py-5">
    <section class="mb-5 text-center">
      <h1 class="display-4 mb-3">About Us</h1>
      <p class="h4 lead">
        This platform is a collaborative course project developed by a team of seven students for a Software Engineering
        class.
        Our mission is to empower instructors with a robust tool to monitor student progress on academic projects,
        leveraging AI insights and real-time collaboration for seamless project management.
      </p>
    </section>

    <section class="team-section mb-5">
      <h2 class="h2 text-center mb-4">Team Roles</h2>
      <div class="row">
        <div v-for="role in teamRoles" :key="role.title" class="col-md-6 mb-3">
          <div class="card shadow-sm">
            <div class="card-body">
              <h5 class="card-title">{{ role.title }}</h5>
              <p class="card-text">{{ role.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="technologies-section">
      <h2 class="h2 text-center mb-4">Technologies Used</h2>
      <div class="row justify-content-center">
        <div v-for="(techGroup, index) in technologyGroups" :key="index" class="col-md-4 mb-3">
          <div class="card h-100">
            <div class="card-body">
              <h5 class="card-title text-center">{{ techGroup.title }}</h5>
              <ul class="list-unstyled text-center">
                <li v-for="tech in techGroup.technologies" :key="tech">{{ tech }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
  .about-page {
    color: rgb(from var(--navbar-bg) r g b/0.8);
  }

  h1,
  h2 {
    color: rgb(from var(--navbar-bg) r g b/0.8);
    font-weight: bold;
  }

  .team-section .card {
    border: none;
    background: #f8f9fa;
  }

  .card-title {
    font-size: 1.2rem;
    font-weight: bold;
  }

  .card-text {
    font-size: 0.95rem;
    color: #6c757d;
  }

  .technologies-section .card {
    border: none;
    background-color: #f8f9fa;
    box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
  }

  .card-body {
    padding: 1.5rem;
  }

  .card-title {
    font-size: 1.3rem;
    font-weight: bold;
    color: rgb(from var(--navbar-bg) r g b/0.8);
  }

  ul {
    list-style-type: none;
    padding-left: 0;
  }

  ul li {
    font-size: 1rem;
    color: #555;
    padding: 5px 0;
  }
</style>
