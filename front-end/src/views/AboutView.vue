<template>
  <div class="about-page container py-5">
    <section class="mb-5">
      <h1 class="display-4 mb-3">About Us</h1>
      <p class="lead">
        This platform is a course project created by a team of seven students for a Software Engineering class. Our goal
        is to provide instructors with a powerful tool to monitor student progress on academic projects, leveraging AI
        insights and real-time collaboration.
      </p>
    </section>

    <section class="team-section mb-5">
      <h2 class="h4 mb-4">Team Roles</h2>
      <ul class="list-group">
        <li class="list-group-item" v-for="role in teamRoles" :key="role.title">
          <strong>{{ role.title }}:</strong> {{ role.description }}
        </li>
      </ul>
    </section>

    <section class="technologies-section">
      <h2 class="h4 mb-4">Technologies Used</h2>
      <ul class="list-inline">
        <li class="list-inline-item badge bg-primary text-white mx-1" v-for="tech in technologies" :key="tech">
          {{ tech }}
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup>
  import { ref } from 'vue'

  const teamRoles = ref( [
    { title: 'Scrum Master', description: 'Facilitates team operations and ensures smooth progress.' },
    { title: 'Project Manager', description: 'Manages tasks, deadlines, and resource allocation.' },
    { title: 'Backend Developer', description: 'Builds and manages server-side functionality.' },
    { title: 'Frontend Developer', description: 'Creates the user interface and experience.' },
    { title: 'Tester', description: 'Ensures quality and reliability through rigorous testing.' }
  ] )

  const technologies = ref( [ 'Figma', 'Canva', 'Vue 3', 'Flask', 'Bootstrap' ] )
</script>

<style scoped>
  .about-page {
    color: #333;
  }

  h1,
  h2 {
    color: #3c3c3c;
  }

  .team-section .list-group-item {
    background: #f7f7f7;
    border: none;
  }

  .technologies-section .badge {
    font-size: 1rem;
    padding: 0.6em 1em;
  }
</style>
