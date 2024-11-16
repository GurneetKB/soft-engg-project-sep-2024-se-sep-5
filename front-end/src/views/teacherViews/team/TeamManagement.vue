<script setup>
  import { ref, computed, onMounted } from 'vue'
  import { fetchfunct } from '@/components/fetch.js'
  import LoadingPlaceholder from '@/components/LoadingPlaceholder.vue'
  import { jsPDF } from "jspdf"

  const teams = ref( [] )
  const currentPage = ref( 1 )
  const itemsPerPage = ref( 5 )
  const searchQuery = ref( '' )
  const sortField = ref( 'rank' )
  const sortOrder = ref( 'asc' )
  const loading = ref( true )
  const error = ref( null )

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
      case 'off_track': return 'text-danger'
      case 'at_risk': return 'text-warning'
      default: return 'text-secondary'
    }
  }

  const openModal = () =>
  {
    new bootstrap.Modal( '#rankingReasonModal' ).show()
  }

  const exportToPDF = () =>
  {
    const doc = new jsPDF()
    let yOffset = 20

    // Set font
    doc.setFont( "helvetica", "normal" )

    // Title
    doc.setFontSize( 18 )
    doc.text( "Team Ranking Reasons", 105, yOffset, { align: "center" } )
    yOffset += 15

    // Team details
    doc.setFontSize( 12 )
    teams.value.forEach( ( team, index ) =>
    {
      if ( yOffset > 270 )
      {
        doc.addPage()
        yOffset = 20
      }

      doc.setFont( "helvetica", "bold" )
      doc.text( `${ index + 1 }. ${ team.team_name }`, 10, yOffset )
      yOffset += 7

      doc.setFont( "helvetica", "normal" )
      doc.text( `Rank: ${ team.rank }`, 15, yOffset )
      yOffset += 7

      doc.text( `Status: ${ team.status.replace( '_', ' ' ).toUpperCase() }`, 15, yOffset )
      yOffset += 7

      doc.text( `Progress: ${ team.progress }%`, 15, yOffset )
      yOffset += 7

      const reasonLines = doc.splitTextToSize( `Reason: ${ team.reason }`, 180 )
      doc.text( reasonLines, 15, yOffset )
      yOffset += 7 * reasonLines.length + 10
    } )

    // Save the PDF
    doc.save( "team_ranking_reasons.pdf" )
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
      <h2 class="main-title text-center mb-4">Team Management</h2>
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-center mb-4">
        <div class="search-container mb-3 mb-md-0">
          <input type="text" v-model.trim="searchQuery" class="search-input form-control"
            placeholder="Search teams..." />
          <i class="bi bi-search search-icon"></i>
        </div>
        <div class="sort-container d-flex align-items-center">
          <button class="btn nav-color-btn me-2" :disabled="loading" @click="openModal">
            Ranking Reason
          </button>
          <button title="sort by rank" class="btn btn-outline-primary me-2" @click="toggleSort('rank')">
            <i
              :class="sortField === 'rank' ? (sortOrder === 'asc' ? 'bi bi-sort-numeric-down' : 'bi bi-sort-numeric-up-alt') : 'bi bi-filter'"></i>
          </button>
          <button title="sort by name" class="btn btn-outline-primary" @click="toggleSort('team_name')">
            <i
              :class="sortField === 'team_name' ? (sortOrder === 'asc' ? 'bi bi-sort-alpha-down' : 'bi bi-sort-alpha-up-alt') : 'bi bi-filter'"></i>
          </button>
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
        </div>
        <div class="pagination d-flex justify-content-center mt-5">
          <button class="btn btn-outline-primary mx-2" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">
            <i class="bi bi-chevron-left"></i> Previous
          </button>
          <button v-for="page in pageNumbers" :key="page" class="btn mx-1"
            :class="{ 'btn-primary': page === currentPage, 'btn-outline-primary': page !== currentPage }"
            @click="goToPage(page)">
            {{ page }}
          </button>
          <button class="btn btn-outline-primary mx-2"
            :disabled="currentPage === totalPages || paginatedTeams.length === 0" @click="goToPage(currentPage + 1)">
            Next <i class="bi bi-chevron-right"></i>
          </button>
        </div>
      </div>
    </div>

    <div class="modal fade" tabindex="-1" role="dialog" id="rankingReasonModal">
      <div class="modal-dialog modal-dialog-scrollable modal-lg" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Ranking Reasons</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal">
            </button>
          </div>
          <div id="ranking-reason-content" class="modal-body">
            <div v-for="team in teams" :key="team.team_id" class="mb-3">
              <p><strong>Team Name:</strong> {{ team.team_name }}</p>
              <p><strong>Rank:</strong> {{ team.rank }}</p>
              <p><strong>Reason for Ranking:</strong> {{ team.reason }}</p>
              <hr v-if="team !== teams[teams.length - 1]">
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button type="button" class="btn btn-primary" @click="exportToPDF">Export to PDF</button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
  .search-container {
    position: relative;
    max-width: 300px;
  }

  .search-input {
    width: 100%;
    padding: 0.5rem 2rem 0.5rem 1rem;
    border-radius: 0.25rem;
    font-size: 1rem;
  }

  .search-icon {
    position: absolute;
    right: 0.75rem;
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
    color: #1a5f7a;
    text-transform: uppercase;
    letter-spacing: 2px;
  }

  .team-item {
    background: white;
    padding: 1.5rem;
    border-radius: 0.5rem;
    transition: all 0.3s ease;
    border: 1px solid #eef0f2;
  }

  .team-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  }

  .progress {
    height: 1.2rem;
    border-radius: 0.6rem;
  }

  .progress-bar {
    border-radius: 0.6rem;
  }

  .no-results {
    text-align: center;
    padding: 2rem;
    color: #6c757d;
    font-size: 1.1rem;
  }
</style>