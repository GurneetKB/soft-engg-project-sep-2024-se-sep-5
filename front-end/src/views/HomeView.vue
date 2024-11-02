<template>
  <div>
    <!-- Hero Section -->
    <section class="hero-section text-white py-5">
      <div class="container">
        <div class="row py-5">
          <div class="col-md-8">
            <h1 class="display-4 fw-bold mb-4">Efficiently Monitor Academic Projects</h1>
            <p class="lead mb-4">
              A dedicated platform with AI-driven insights and collaboration tools, built exclusively for educational institutions.
            </p>
            <div class="d-flex gap-3">
              <button class="btn btn-light btn-lg">Request Access</button>
              <router-link to="/about" class="btn btn-outline-light btn-lg">Learn More</router-link>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- User Types Section -->
    <section class="py-5">
      <div class="container">
        <h2 class="text-center mb-5">For Academia</h2>
        <div class="row g-4">
          <div class="col-md-4" v-for="user in userTypes" :key="user.title">
            <div class="card h-100 shadow-sm">
              <div class="card-body">
                <div class="d-flex align-items-center mb-3">
                  <i :class="user.icon" class="fs-4 me-2 text-secondary"></i>
                  <h3 class="card-title h5 mb-0">{{ user.title }}</h3>
                </div>
                <p class="card-text">{{ user.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section py-5">
      <div class="container">
        <h2 class="text-center mb-5">Core Capabilities</h2>
        <div class="row g-4">
          <div class="col-md-6 col-lg-3" v-for="feature in features" :key="feature.title">
            <div class="card h-100 text-center shadow-sm">
              <div class="card-body">
                <i :class="feature.icon" class="fs-1 text-primary mb-3"></i>
                <h3 class="card-title h5">{{ feature.title }}</h3>
                <p class="card-text">{{ feature.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const userTypes = ref([
  { title: 'Instructors', icon: 'bi bi-book', description: 'Track projects and provide feedback in a secure academic platform.' },
  { title: 'Teaching Assistants', icon: 'bi bi-people', description: 'Assist students with structured support for code and queries.' },
  { title: 'Students', icon: 'bi bi-graph-up', description: 'Track progress, submit assignments, and receive feedback.' }
])

const features = ref([
  { title: 'Secure GitHub Integration', icon: 'bi bi-github', description: 'Monitor project progress securely.' },
  { title: 'AI Document Analysis', icon: 'bi bi-cpu', description: 'AI insights for document and code reviews.' },
  { title: 'Progress Monitoring', icon: 'bi bi-bar-chart-line', description: 'Real-time progress tracking.' },
  { title: 'Built-in Collaboration', icon: 'bi bi-chat-dots', description: 'Structured communication tools for guidance.' }
])
</script>

<style scoped>
/* Hero Section Styling with new colors */
.hero-section {
  background: linear-gradient(135deg, #4a148c, #00695c);
}

/* Card Styling */
.card {
  transition: transform 0.3s ease;
}
.card:hover {
  transform: translateY(-5px);
}
</style>
