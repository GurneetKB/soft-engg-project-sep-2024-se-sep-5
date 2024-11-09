<script setup>
  import { ref, computed, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { fetchfunct } from '@/components/fetch'
  import { useIdentityStore } from '@/stores/identity'
  import { storeToRefs } from 'pinia'

  const router = useRouter()
  const { identity } = storeToRefs( useIdentityStore() )

  // State
  const milestones = ref( [] )
  const noOfStudents = ref( 0 )
  const noOfTeams = ref( 0 )
  const error = ref( null )

  // Computed
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

  // Methods
  const getAllMilestones = async () =>
  {
    const res = await fetchfunct( 'api/instructor/all_milestone' )

    if ( res.ok )
    {
      milestones.value = await res.json()
      const response = await fetchfunct( 'teacher/milestone_management/numbers' )
      if ( response.ok )
      {
        const data = await response.json()
        noOfStudents.value = data.no_of_students
        noOfTeams.value = data.no_of_teams
      }
    } else
    {
      error.value = res.status
    }
  }

  const deleteMilestone = async ( milestone_id ) =>
  {
    if ( confirm( 'Do you really want to delete?' ) )
    {
      const res = await fetchfunct(
        `api/instructor/milestone/${ milestone_id }`,
        {
          method: 'DELETE',
        },
      )

      if ( res.ok )
      {
        router.go( 0 )
      } else
      {
        error.value = res.status
      }
    }
  }

  // Lifecycle
  onMounted( () =>
  {
    getAllMilestones()
  } )
</script>

<template>
  <router-view v-if="$route.name !== 'MilestoneManagement'"></router-view>
  <div v-else>
    <section class="py-5">
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
        <div class="milestone-wrapper">
          <div v-for="milestone in milestonesWithStatus" :key="milestone.name" class="milestone-item mb-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="milestone-title mb-0">{{ milestone.title }}</h5>
              <span class="progress-text">{{ milestone.completion_rate }}%</span>
              <div class="d-flex gap-2" v-if="identity.includes('Instructor')">
                <RouterLink class="btn btn-outline-primary btn-sm"
                  :to="`/teacher/milestone_management/edit_milestone/${milestone.id}`">
                  <i class="bi bi-pencil-square"></i>
                </RouterLink>
                <button class="btn btn-outline-danger btn-sm" @click="deleteMilestone(milestone.id)">
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