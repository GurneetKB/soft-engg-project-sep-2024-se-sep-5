<template>
  <section class="py-5">
    <div class="container hero-section py-5 rounded-lg px-4 shadow-lg">
      <div class="text-center mb-5 position-relative">
        <div class="d-flex justify-content-between align-items-center">
          <h2 class="main-title text-center flex-grow-1">Team Management</h2>
          <div class="search-container" style="max-width: 300px">
            <input
              type="text"
              v-model.trim="searchQuery"
              class="search-input"
              placeholder="Search teams..."
            />
            <i class="fas fa-search search-icon"></i>
          </div>
        </div>
      </div>
      <div class="team-wrapper">
        <div v-if="paginatedTeams.length === 0" class="no-results">
          No teams found matching your search.
        </div>
        <div
          v-else
          v-for="team in paginatedTeams"
          :key="team.title"
          class="team-item mb-4"
        >
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="team-title mb-0">{{ team.title }}</h5>
            <span class="progress-text">{{ team.progress }}%</span>
          </div>
          <div class="progress">
            <div
              :class="'progress-bar progress-bar-' + team.status"
              role="progressbar"
              :style="{ width: team.progress + '%' }"
            ></div>
          </div>
        </div>
        <div class="pagination d-flex justify-content-center mt-5">
          <button
            class="btn btn-primary mx-2"
            :disabled="currentPage === 1"
            @click="currentPage--"
          >
            <i class="fas fa-chevron-left"></i> Previous
          </button>
          <button
            class="btn btn-primary mx-2"
            :disabled="currentPage === totalPages"
            @click="currentPage++"
          >
            Next <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  data() {
    return {
      teams: [],
      currentPage: 1,
      itemsPerPage: 5,
      searchQuery: '',
    }
  },
  computed: {
    filteredTeams() {
      return this.teams
        .filter(team =>
          team.title.toLowerCase().includes(this.searchQuery.toLowerCase()),
        )
        .sort((a, b) => a.title.localeCompare(b.title))
    },
    totalPages() {
      return Math.ceil(this.filteredTeams.length / this.itemsPerPage)
    },
    paginatedTeams() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return this.teamsWithStatus(this.filteredTeams).slice(start, end)
    },
  },
  methods: {
    teamsWithStatus(teams) {
      return teams.map(team => {
        let status = 'light'
        if (team.progress === 100) {
          status = 'success'
        } else if (team.progress > 50) {
          status = 'warning'
        } else if (team.progress > 0 && team.progress <= 50) {
          status = 'danger'
        }
        return { ...team, status }
      })
    },
  },
  mounted() {
    this.teams = [
      { title: 'Alpha Team', progress: 100 },
      { title: 'Beta Team', progress: 75 },
      { title: 'Delta Team', progress: 50 },
      { title: 'Gamma Team', progress: 25 },
      { title: 'Echo Team', progress: 90 },
      { title: 'Falcon Team', progress: 60 },
      { title: 'Hawk Team', progress: 40 },
      { title: 'Ice Team', progress: 85 },
      { title: 'Jupiter Team', progress: 30 },
      { title: 'Kilo Team', progress: 70 },
      { title: 'Lima Team', progress: 95 },
      { title: 'Metro Team', progress: 20 },
    ]
  },
}
</script>

<style scoped>
.search-container {
  position: relative;
  max-width: 500px;
  margin: 2rem auto;
}

.search-input {
  width: 100%;
  padding: 1rem 2.5rem;
  border: 2px solid #e0e0e0;
  border-radius: 50px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: #f8f9fa;
}

.search-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
}

.hero-section {
  background: linear-gradient(to bottom right, #ffffff, #f8f9fa);
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.main-title {
  font-size: 2.5rem;
  font-weight: 800;
  background: #1a5f7a;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 1rem;
}

.team-item {
  background: white;
  padding: 25px;
  border-radius: 15px;
  transition: all 0.3s ease;
  border: 1px solid #eef0f2;
}

.team-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.progress-bar-success {
  background: #20c997;
}

.progress-bar-warning {
  background: #ffd966;
}

.progress-bar-danger {
  background: #f86b6b;
}

.progress-bar-light {
  background: #6c757d;
}

.btn-primary {
  background: #007bff;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 50px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
  transform: translateY(-2px);
}

.no-results {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
  font-size: 1.1rem;
}

.progress {
  height: 1.2rem;
  border-radius: 10px;
}
</style>
