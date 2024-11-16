<script setup>
  import { ref, computed, onMounted } from 'vue'
  import { fetchfunct } from '@/components/fetch.js'
  import LoadingPlaceholder from '@/components/LoadingPlaceholder.vue'
  import html2pdf from 'html2pdf.js'

  const teams = ref( [] )
  const currentPage = ref( 1 )
  const itemsPerPage = ref( 5 )
  const searchQuery = ref( '' )
  const sortField = ref( 'rank' )
  const sortOrder = ref( 'asc' )
  const loading = ref( true )
  const error = ref( null )
  const showReason = ref( {} )

  const filteredTeams = computed( () =>
  {
    return teams.value
      .filter( team =>
        team.team_name.toLowerCase().includes( searchQuery.value.toLowerCase() )
      )
      .sort( ( a, b ) =>
      {
        const modifier = sortOrder.value === 'asc' ? 1 : -1
        if ( a[ sortField.value ] < b[ sortField.value ] ) return -1 * modifier
        if ( a[ sortField.value ] > b[ sortField.value ] ) return 1 * modifier
        return 0
      } )
  } )

  const totalPages = computed( () =>
  {
    return Math.ceil( filteredTeams.value.length / itemsPerPage.value )
  } )

  const paginatedTeams = computed( () =>
  {
    const start = ( currentPage.value - 1 ) * itemsPerPage.value
    const end = start + itemsPerPage.value
    return filteredTeams.value.slice( start, end )
  } )

  const pageNumbers = computed( () =>
  {
    return Array.from( { length: totalPages.value }, ( _, i ) => i + 1 )
  } )

  const toggleSort = ( field ) =>
  {
    if ( sortField.value === field )
    {
      sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    } else
    {
      sortField.value = field
      sortOrder.value = 'asc'
    }
  }

  const toggleReason = ( teamId ) =>
  {
    showReason.value[ teamId ] = !showReason.value[ teamId ]
  }

  const goToPage = ( page ) =>
  {
    if ( page >= 1 && page <= totalPages.value )
    {
      currentPage.value = page
    }
  }

  const getStatusColor = ( status ) =>
  {
    switch ( status )
    {
      case 'on_track': return 'text-success'
      case 'behind': return 'text-warning'
      case 'at_risk': return 'text-danger'
      default: return 'text-secondary'
    }
  }

  const exportToPDF = () =>
  {
    const element = document.getElementById( 'team-management-content' )
    html2pdf( element )
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
      error.value = err.message
    }
    loading.value = false
  } )
</script>

<template>
  <section class="py-5">
    <div id="team-management-content" class="container hero-section py-5 rounded-lg px-4 shadow-lg">
      <div class="text-center mb-5 position-relative">
        <div class="d-flex justify-content-between align-items-center flex-wrap">
          <h2 class="main-title text-center flex-grow-1">Team Management</h2>
          <div class="search-container mt-2 mt-md-0" style="max-width: 300px">
            <input type="text" v-model.trim="searchQuery" class="search-input" placeholder="Search teams..." />
            <i class="fas fa-search search-icon"></i>
          </div>
          <div class="sort-container ms-3 mt-2 mt-md-0">
            <button class="btn btn-outline-primary me-2" @click="toggleSort('rank')">
              Sort by Rank <i
                :class="sortField === 'rank' ? (sortOrder === 'asc' ? 'fas fa-sort-up' : 'fas fa-sort-down') : 'fas fa-sort'"></i>
            </button>
            <button class="btn btn-outline-primary" @click="toggleSort('team_name')">
              Sort by Name <i
                :class="sortField === 'team_name' ? (sortOrder === 'asc' ? 'fas fa-sort-up' : 'fas fa-sort-down') : 'fas fa-sort'"></i>
            </button>
          </div>
        </div>
      </div>
      <div class="team-wrapper">
        <LoadingPlaceholder v-if="loading" variant="list-item" :count="5" />

        <div v-else-if="error" class="alert alert-danger">
          {{ error }}
        </div>
        <div v-else-if="paginatedTeams.length === 0" class="no-results">
          No teams found matching your search.
        </div>
        <div v-else v-for="team in paginatedTeams" :key="team.team_id" class="team-item mb-4 p-3 border rounded">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="team-name mb-0">{{ team.team_name }}</h5>
            <span class="rank-text">Rank: {{ team.rank }}</span>
          </div>

          <div class="progress mb-2">
            <div class="progress-bar" role="progressbar" :style="{ width: team.progress + '%' }" :class="{
                   'bg-success': team.progress === 100,
                   'bg-warning': team.progress > 50 && team.progress < 100,
                   'bg-danger': team.progress <= 50
                 }">
              {{ team.progress }}%
            </div>
          </div>
          <div class="status mt-2">
            <strong>Status:</strong> <span
              :class="getStatusColor(team.status)">{{ team.status.replace('_', ' ').toUpperCase() }}</span>
          </div>
          <div class="mt-2">
            <button class="btn btn-sm btn-info" @click="toggleReason(team.team_id)">
              {{ showReason[team.team_id] ? 'Hide' : 'Show' }} Reason for Ranking
            </button>
          </div>
          <div v-if="showReason[team.team_id]" class="mt-2 p-2 bg-light rounded">
            <strong>Reason:</strong> {{ team.reason }}
          </div>
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
      <div class="mt-4 text-center">
        <button class="btn btn-success" @click="exportToPDF">
          Export to PDF
        </button>
      </div>
    </div>
  </section>
</template>

<style scoped>
  .search-container {
    position: relative;
  }

  .search-input {
    padding-right: 30px;
    width: 100%;
  }

  .search-icon {
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
  }

  .team-item {
    transition: all 0.3s ease;
  }

  .team-item:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }

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