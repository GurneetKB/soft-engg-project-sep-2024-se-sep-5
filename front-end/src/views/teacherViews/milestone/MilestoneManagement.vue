<script setup>
  import { ref, computed, onMounted, watch } from 'vue'
  import { checkerror, checksuccess, fetchfunct } from '@/components/fetch'
  import { useIdentityStore } from '@/stores/identity'
  import { storeToRefs } from 'pinia'
  import { useRoute } from 'vue-router'
  import LoadingPlaceholder from '@/components/LoadingPlaceholder.vue'
  const { identity } = storeToRefs( useIdentityStore() )

  const milestones = ref( [] )
  const deleteMilestoneId = ref( null )
  const noOfStudents = ref( 0 )
  const noOfTeams = ref( 0 )
  const error = ref( null )
  const loading = ref( false )

  const milestonesWithStatus = computed( () =>
  {
    return milestones.value.map( milestone =>
    {
      let status = 'light'
      if ( milestone.completion_rate === 100 )
      {
        status = 'success'
      } else if ( milestone.completion_rate > 50 )
      {
        status = 'warning'
      } else if ( milestone.completion_rate > 0 && milestone.completion_rate <= 50 )
      {
        status = 'danger'
      }
      return { ...milestone, status }
    } )
  } )

  const handleDeleteButtonClick = ( milestoneId ) =>
  {
    new bootstrap.Modal( '#deleteConfirmation' ).show()
    deleteMilestoneId.value = milestoneId
  }

  const deleteMilestone = async () =>
  {
    bootstrap.Modal.getInstance( document.getElementById( 'deleteConfirmation' ) ).hide()
    const res = await fetchfunct(
      `teacher/milestone_management/${ deleteMilestoneId.value }`,
      {
        method: 'DELETE',
      } )

    if ( res.ok )
    {
      checksuccess( res )
      milestones.value = milestones.value.filter(
        ( milestone ) => milestone.id !== deleteMilestoneId.value
      );

    } else
    {
      checkerror( res )
    }
  }

  const fetchMilestones = async () =>
  {
    loading.value = true
    const res = await fetchfunct( 'teacher/milestone_management' )

    if ( res.ok )
    {
      const data = await res.json()
      milestones.value = data.milestones
      noOfStudents.value = data.no_of_students
      noOfTeams.value = data.no_of_teams
    } else
    {
      error.value = "Failed to fetch milestone details"
    }
    loading.value = false
  }

  onMounted( () =>
  {
    fetchMilestones()
  } )

  // Watch for route changes and trigger a fetch
  const route = useRoute()
  watch(
    () => route.fullPath,
    ( newPath, oldPath ) =>
    {
      if ( newPath === '/teacher/milestone_management' )
      {
        fetchMilestones()
      }
    }
  )
</script>

<template>
  <router-view v-if="$route.name !== 'MilestoneManagement'"></router-view>
  <div v-else>
    <section class="py-5">
      <div v-if="error" class="alert alert-danger mt-4" role="alert">
        {{ error }}
      </div>
      <div class="container px-4">
        <div class="row g-4 justify-content-center mx-0">
          <div class="col-sm-5 px-2">
            <div class="stats-card rounded-lg shadow-sm">
              <div class="card-body d-flex flex-column align-items-center">
                <h2 class="card-title fw-bold mb-4 text-dark">
                  Total Registered Students
                </h2>
                <div class="stats-number text-primary">
                  {{noOfStudents}}
                </div>
              </div>
            </div>
          </div>
          <div class="col-sm-5 px-2">
            <div class="stats-card rounded-lg shadow-sm">
              <div class="card-body d-flex flex-column align-items-center">
                <h2 class="card-title fw-bold mb-4 text-dark">
                  Total Number of Teams
                </h2>
                <div class="stats-number text-primary">
                  {{noOfTeams}}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="py-5 bg-light">
      <div class="container hero-section py-5 rounded-lg px-4 shadow-sm">
        <div class="text-center mb-4 position-relative">
          <h2 class="main-title text-dark">Milestones</h2>
          <button class="btn btn-success rounded-circle add-button position-absolute"
            v-if="identity.includes('Instructor')" style=" right: 20px; top: 0">
            <RouterLink class="nav-link" to="/teacher/milestone_management/add_milestone">
              <i class="bi bi-plus fs-0" style="font-size: 4rem"></i>
            </RouterLink>
          </button>
        </div>

        <div class="modal" tabindex="-1" role="dialog" id="deleteConfirmation">
          <div class="modal-dialog modal-dialog-centered" role="document">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">Confirm Milestone Deletion</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
              </div>
              <div class="modal-body">
                <p>Are you sure you want to delete the milestone?</p>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                  Cancel
                </button>
                <button type="button" class="btn nav-color-btn" @click="deleteMilestone">
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="milestone-wrapper">
          <LoadingPlaceholder v-if="loading" variant="list-item" :count="5" />
          <div v-else v-for="milestone in milestonesWithStatus" :key="milestone.name" class="milestone-item mb-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="milestone-title mb-0">{{ milestone.title }}</h5>
              <span class="progress-text ms-auto me-2">{{ milestone.completion_rate }}%</span>
              <div class="d-flex gap-2" v-if="identity.includes('Instructor')">
                <RouterLink class="btn btn-outline-primary btn-sm"
                  :to="`/teacher/milestone_management/edit_milestone/${milestone.id}`">
                  <i class="bi bi-pencil-square"></i>
                </RouterLink>
                <button class="btn btn-outline-danger btn-sm" @click="handleDeleteButtonClick(milestone.id)">
                  <i class="bi bi-trash"></i>
                </button>
              </div>
            </div>
            <div class="progress">
              <div :class="'progress-bar progress-bar-' + milestone.status" role="progressbar"
                :style="{ width: milestone.completion_rate + '%' }">
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
  .add-button {
    width: 70px;
    height: 70px;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  }

  .hero-section {
    background: #ffffff;
    border-radius: 20px;
  }

  .stats-card {
    background: #ffffff;
    padding: 2rem;
    border: 1px solid #ddd;
    border-radius: 15px;
    transition: all 0.3s ease;
  }

  .main-title {
    font-size: 2rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #333;
  }

  .stats-number {
    font-size: 2.5rem;
    font-weight: bold;
    padding: 1rem 2rem;
    background: rgba(0, 123, 255, 0.1);
    color: #007bff;
    border-radius: 10px;
  }

  .milestone-wrapper {
    max-width: 700px;
    margin: 0 auto;
    padding: 0 20px;
  }

  .milestone-item {
    background: rgba(0, 0, 0, 0.03);
    padding: 20px;
    border-radius: 10px;
  }

  .milestone-title {
    font-weight: 600;
    margin-bottom: 10px;
    color: #333;
  }

  .progress {
    height: 1rem;
    background: rgba(0, 0, 0, 0.05);
    border-radius: 5px;
  }

  .progress-bar-success {
    background-color: #a8d5ba;
  }

  .progress-bar-warning {
    background-color: #ffd966;
  }

  .progress-bar-danger {
    background-color: #ffb3b3;
  }

  .card-title {
    font-size: 1.2rem;
    text-align: center;
    color: #333;
  }
</style>