<script setup>
  import { ref, computed, onMounted } from 'vue'
  import { fetchfunct } from '@/components/fetch.js'
  import LoadingPlaceholder from '@/components/LoadingPlaceholder.vue'

  const teams = ref( [] )
  const currentPage = ref( 1 )
  const itemsPerPage = ref( 5 )
  const searchQuery = ref( '' )
  const loading = ref( true )
  const error = ref( null )

  const filteredTeams = computed( () =>
  {
    return teams.value
      .filter( team =>
        team.name.toLowerCase().includes( searchQuery.value.toLowerCase() )
      )
      .sort( ( a, b ) => a.name.localeCompare( b.name ) )
  } )

  const totalPages = computed( () =>
  {
    return Math.ceil( filteredTeams.value.length / itemsPerPage.value )
  } )

  const paginatedTeams = computed( () =>
  {
    const start = ( currentPage.value - 1 ) * itemsPerPage.value
    const end = start + itemsPerPage.value
    return teamsWithStatus( filteredTeams.value ).slice( start, end )
  } )

  const pageNumbers = computed( () =>
  {
    return Array.from( { length: totalPages.value }, ( _, i ) => i + 1 )
  } )

  const teamsWithStatus = ( teams ) =>
  {
    return teams.map( team =>
    {
      let status = 'light'
      if ( team.progress === 100 )
      {
        status = 'success'
      } else if ( team.progress > 50 )
      {
        status = 'warning'
      } else if ( team.progress > 0 && team.progress <= 50 )
      {
        status = 'danger'
      }
      return { ...team, status }
    } )
  }

  const goToPage = ( page ) =>
  {
    if ( page >= 1 && page <= totalPages.value )
    {
      currentPage.value = page
    }
  }

  onMounted( async () =>
  {
    loading.value = true
    const response = await fetchfunct( 'teacher/team_management/overall' )
    if ( response.ok )
    {
      teams.value = await response.json()
    } else
    {
      error.value = 'Failed to fetch milestones'
    }
    loading.value = false
  } )
</script>

<template>
  <section class="py-5">
    <div class="container hero-section py-5 rounded-lg px-4 shadow-lg">
      <div class="text-center mb-5 position-relative">
        <div class="d-flex justify-content-between align-items-center">
          <h2 class="main-title text-center flex-grow-1">Team Management</h2>
          <div class="search-container" style="max-width: 300px">
            <input type="text" v-model.trim="searchQuery" class="search-input" placeholder="Search teams..." />
            <i class="fas fa-search search-icon"></i>
          </div>
        </div>
      </div>
      <div class="team-wrapper">
        <LoadingPlaceholder v-if="loading" variant="text" :count="3" :lines="[2]" spacing="p-4" :withBorder="true" />

        <div v-else-if="error" class="alert alert-danger">
          {{ error }}
        </div>
        <div v-if="paginatedTeams.length === 0 && !loading" class="no-results">
          No teams found matching your search.
        </div>
        <div v-else v-for="team in paginatedTeams" :key="team.name" class="team-item mb-4">
          <router-link to="/teacher/team_management/progress" class="text-decoration-none text-dark">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="team-name mb-0">{{ team.name }}</h5>
              <span class="progress-text">{{ team.progress }}%</span>
            </div>

            <div class="progress">
              <div :class="'progress-bar progress-bar-' + team.status" role="progressbar"
                :style="{ width: team.progress + '%' }"></div>
            </div>
          </router-link>
        </div>
        <div class="pagination d-flex justify-content-center mt-5">
          <button class="btn btn-outline-primary mx-2" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">
            <i class="fas fa-chevron-left"></i> Previous
          </button>
          <button v-for="page in pageNumbers" :key="page" class="btn mx-1"
            :class="{ 'btn-primary': page === currentPage, 'btn-outline-primary': page !== currentPage }"
            @click="goToPage(page)">
            {{ page }}
          </button>
          <button class="btn btn-outline-primary mx-2"
            :disabled="currentPage === totalPages || paginatedTeams.length === 0" @click="goToPage(currentPage + 1)">
            Next <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </div>
    </div>
  </section>
</template>


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
    background-clip: text;
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