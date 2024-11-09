<script setup>
    import { ref, onMounted } from 'vue'
    import { fetchfunct } from '@/components/fetch.js'
    import SearchableDropdown from '@/components/SearchableDropdown.vue';
    import LoadingPlaceholder from '@/components/LoadingPlaceholder.vue'

    const teams = ref( [] )
    const selectedTeamId = ref( null )
    const teamDetails = ref( [] )
    const loadingOnMount = ref( true )
    const loading = ref( false )
    const error = ref( null )
    const milestones = ref([
    { name: 'Milestone 1' },
    { name: 'Milestone 2' },
    { name: 'Milestone 3' },
    { name: 'Milestone 4' },
]);
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
            const response = await fetchfunct( `teacher/team_management/individual/github/${ selectedTeamId.value }` )
            if ( response.ok )
            {
            
            const data = await response.json()
            teamDetails.value = data
            milestones.value = data.milestones
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
          <h4 class="m-0">Individual Team Github Details</h4>
        </div>
  
        <LoadingPlaceholder v-if="loadingOnMount" variant="text" :count="3" :lines="[2]" spacing="p-4" :withBorder="true" />
  
        <SearchableDropdown v-model="selectedTeamId" @change="fetchTeamDetails" :options="teams" v-else />
  
        <!-- Show these sections only if a team is selected -->
        <div v-if="selectedTeamId" class="mt-4">
          <!-- Loading spinner while fetching team details -->
          <div v-if="loading" class="d-flex justify-content-center my-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
  
          <!-- Error message if fetching team details fails -->
          <div v-if="error" class="alert alert-danger mt-4" role="alert">
            {{ error }}
          </div>
  
          <!-- Team details (GitHub activity and milestones) -->
          <div v-if="teamDetails" class="github-commits card">
            <br>
            <h3>GitHub Activities</h3>
            <h5>GitHub Commits: {{ teamDetails.totalCommits }}</h5>
            <h5>Lines added: {{ teamDetails.linesOfCodeAdded }}</h5>
            <h5>Lines deleted: {{ teamDetails.linesOfCodeDeleted }}</h5>
            <br>
          </div>
  
          <!-- Timeline for milestones -->
          <div class="timeline">
            <div v-for="(milestone, index) in milestones" :key="index" class="milestone">
              <div class="circle"></div>
              <p class="milestone-name">{{ milestone.name }}</p>
              <p class="milestone-commits">Commits: {{ milestone.commits }}</p>
              <p class="milestone-commits">Added: {{ milestone.linesOfCodeAdded }}</p>
              <p class="milestone-commits">Deleted: {{ milestone.linesOfCodeDeleted }}</p>
              <div v-if="index < milestones.length - 1" class="progress-line"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <style scoped>
  .github-commits {
    text-align: center;
  }
  .timeline {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 20px;
    position: relative;
  }
  .milestone {
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
    width: 100%;
  }
  .circle {
    width: 20px;
    height: 20px;
    background-color: black;
    border-radius: 50%;
    margin-bottom: 5px;
  }
  .milestone-name {
    font-weight: bold;
    margin-top: 5px;
  }
  .milestone-commits {
    color: gray;
  }
  .progress-line {
    width: calc(100% - 40px); /* Adjust for padding between milestones */
    height: 2px;
    background-color: lightgray;
    position: absolute;
    top: 10px; /* Adjust to align with circles */
    left: 50%;
    transform: translateX(50%);
    z-index: -1;
  }
  .milestone + .milestone .progress-line {
    display: block;
  }
  </style>