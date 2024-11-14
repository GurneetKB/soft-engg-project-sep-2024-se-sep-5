<script setup>
  import { ref, onMounted, watch, nextTick } from 'vue'
  import { checkerror, fetchfunct } from '@/components/fetch.js'
  import SearchableDropdown from '@/components/SearchableDropdown.vue'
  import LoadingPlaceholder from '@/components/LoadingPlaceholder.vue'

  const teams = ref( [] )
  const selectedTeamId = ref( null )
  const members = ref( [] )
  const selectedMember = ref( null )
  const teamDetails = ref( null )
  const loadingOnMount = ref( true )
  const loading = ref( false )
  const error = ref( null )
  const milestones = ref( [] )

  onMounted( async () =>
  {
    loadingOnMount.value = true

    const response = await fetchfunct( 'teacher/team_management/individual' )
    if ( response.ok )
    {
      const data = await response.json()
      teams.value = data.teams
    } else
    {
      error.value = 'Failed to fetch teams'
    }
    loadingOnMount.value = false

  } )

  const fetchTeamMembers = async () =>
  {
    if ( selectedTeamId.value !== null )
    {
      loading.value = true
      error.value = null
      selectedMember.value = null // Reset selected member when changing teams
      members.value = [] // Clear previous members

      const response = await fetchfunct( `teacher/team_management/individual/detail/${ selectedTeamId.value }` )
      if ( response.ok )
      {
        const data = await response.json()
        members.value = [ { id: null, name: 'All Members' }, ...data.team.members ]
      } else
      {
        checkerror( response )
      }
      loading.value = false
    }
  }

  const fetchTeamGithubDetails = async () =>
  {
    if ( selectedTeamId.value !== null )
    {
      loading.value = true
      error.value = null
      teamDetails.value = null
      milestones.value = []

      const response = await fetchfunct(
        `teacher/team_management/individual/github/${ selectedTeamId.value }`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify( { user_id: selectedMember.value } )
        }
      )
      if ( response.ok )
      {
        const data = await response.json()
        teamDetails.value = data
        milestones.value = data.milestones
      } else
      {
        checkerror( response )
      }

      loading.value = false
    }

  }

  // Watch for changes in selectedTeamId to fetch members
  watch( selectedTeamId, async ( newValue ) =>
  {
    if ( newValue !== null )
    {
      await fetchTeamMembers()
      // Use nextTick to ensure DOM is updated before fetching GitHub details
      nextTick( () =>
      {
        fetchTeamGithubDetails()
      } )
    }
  } )

  // Watch for changes in selectedMember to fetch GitHub details
  watch( selectedMember, fetchTeamGithubDetails )
</script>

<template>
  <div class="container-fluid p-4">
    <div class="team-progress-view max-w-800 mx-auto">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h4 class="m-0">Individual Team Github Details</h4>
      </div>

      <LoadingPlaceholder v-if="loadingOnMount" variant="list-item" :count="5" />

      <template v-else>
        <SearchableDropdown v-model="selectedTeamId" :options="teams" label="Select Team" />

        <div v-if="selectedTeamId" class="mt-4">
          <SearchableDropdown v-model="selectedMember" :options="members" label="Select Team Member"
            :disabled="loading || members.length === 0" />

          <div v-if="loading" class="d-flex justify-content-center my-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>

          <div v-if="error" class="alert alert-danger mt-4" role="alert">
            {{ error }}
          </div>

          <div v-if="teamDetails && !loading" class="github-commits card mb-4 mt-4">
            <div class="card-body text-center">
              <h3>GitHub Activities</h3>
              <h5>GitHub Commits: {{ teamDetails.totalCommits }}</h5>
              <h5>Lines added: {{ teamDetails.linesOfCodeAdded }}</h5>
              <h5>Lines deleted: {{ teamDetails.linesOfCodeDeleted }}</h5>
            </div>
          </div>

          <div class="timeline">
            <div v-for="(milestone, index) in milestones" :key="index" class="timeline-item">
              <div class="timeline-icon">
                <span class="badge">✓</span>
              </div>
              <div class="timeline-content">
                <div class="card mb-4">
                  <div class="card-header">
                    <div class="d-flex justify-content-between align-items-center">
                      <h5 class="card-title mb-0">{{ milestone.name }}</h5>
                      <span class="badge bg-primary">Milestone</span>
                    </div>
                  </div>
                  <div class="card-body">
                    <p>Commits: {{ milestone.commits }}</p>
                    <p>Lines Added: {{ milestone.linesOfCodeAdded }}</p>
                    <p>Lines Deleted: {{ milestone.linesOfCodeDeleted }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
  .timeline {
    position: relative;
    padding: 20px 0;
  }

  .timeline-item {
    display: flex;
    position: relative;
  }

  .timeline-item::before {
    background: #dee2e6;
    content: '';
    height: 100%;
    left: 19px;
    position: absolute;
    top: 20px;
    width: 2px;
    z-index: -1;
  }

  .timeline-icon {
    margin-right: 15px;
  }

  .timeline-icon .badge {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: var(--navbar-bg);
    color: white;
    margin-top: 20px;
  }

  .timeline-content {
    flex: 1 1 auto;
    padding: 0 0 0 1rem;
  }

  .card {
    max-height: 300px;
    overflow-y: auto;
  }
</style>
