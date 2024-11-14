<script setup>
  import { ref, onMounted } from 'vue'
  import { fetchfunct } from '@/components/fetch.js'
  import SearchableDropdown from '@/components/SearchableDropdown.vue'
  import LoadingPlaceholder from '@/components/LoadingPlaceholder.vue'

  const teams = ref( [] )
  const selectedTeamId = ref( null )
  const teamDetails = ref( null )
  const loadingOnMount = ref( true )
  const loading = ref( false )
  const error = ref( null )

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

  const fetchTeamDetails = async () =>
  {
    if ( selectedTeamId.value !== null )
    {
      loading.value = true
      error.value = null
      const response = await fetchfunct(
        `teacher/team_management/individual/detail/${ selectedTeamId.value }`,
      )
      if ( response.ok )
      {
        teamDetails.value = await response.json()
        error.value = null
      } else
      {
        error.value = 'Error fetching team details'
      }
      loading.value = false
    }
  }
</script>

<template>
  <div class="container-fluid p-4">
    <div class="team-progress-view max-w-800 mx-auto">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h4 class="m-0">Individual Team Details</h4>
      </div>
      <LoadingPlaceholder v-if="loadingOnMount" variant="list-item" :count="5" />
      <SearchableDropdown v-model="selectedTeamId" @change="fetchTeamDetails" :options="teams" v-else>
      </SearchableDropdown>

      <div v-if="loading" class="d-flex justify-content-center my-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <div v-if="error" class="alert alert-danger mt-4" role="alert">
        {{ error }}
      </div>

      <div v-if="teamDetails" class="mt-4">
        <div class="card">
          <div class="card-header text-white">
            <h5 class="card-title mb-0">{{ teamDetails.team.name }}</h5>
          </div>
          <div class="card-body">
            <!-- Team Information section -->
            <div class="mb-4">
              <p>
                <strong>GitHub Repository:</strong>
                <a :href="teamDetails.team.github_repo_url" target="_blank" class="text-primary">
                  {{ teamDetails.team.github_repo_url }}
                </a>
              </p>
              <p>
                <strong>Instructor:</strong>
                {{ teamDetails.team.instructor.username }}
              </p>
              <p>
                <strong>Teaching Assistant:</strong>
                {{ teamDetails.team.ta.username }}
              </p>
            </div>

            <!-- Team Members section -->
            <div>
              <h6 class="mb-3"><strong>Team Members</strong></h6>
              <div class="table-responsive">
                <table class="table table-bordered table-hover">
                  <thead class="table-light">
                    <tr>
                      <th>Username</th>
                      <th>Email</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="member in teamDetails.team.members" :key="member.id">
                      <td>{{ member.username }}</td>
                      <td>{{ member.email }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
  .card {
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    border-radius: 0.5rem;
  }

  .card-header {
    background-color: var(--navbar-bg);
    border-top-left-radius: 0.5rem;
    border-top-right-radius: 0.5rem;
  }

  .table {
    margin-bottom: 0;
  }

  .table th {
    font-weight: 600;
  }
</style>
