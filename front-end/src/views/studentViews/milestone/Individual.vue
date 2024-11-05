<template>
  <div class="individual-milestone-container">
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Individual Milestone</h3>
      </div>
      <div class="card-body">
        <div class="form-group">
          <label for="milestone-select" class="form-label">Select a Milestone</label>
          <select
            id="milestone-select"
            class="form-select"
            v-model="selectedMilestoneId"
            @change="fetchMilestoneDetails"
          >
            <option value="" disabled>Select a milestone</option>
            <option v-for="milestone in milestones" :key="milestone.id" :value="milestone.id">
              {{ milestone.title }}
            </option>
          </select>
        </div>

        <div v-if="milestoneDetails" class="mt-4">
          <h4 class="mb-3">{{ milestoneDetails.title }}</h4>
          <p class="mb-2">{{ milestoneDetails.description }}</p>
          <p class="mb-2">
            <strong>Deadline:</strong> {{ milestoneDetails.deadline }}
          </p>
          <p class="mb-0">
            <strong>Created At:</strong> {{ milestoneDetails.created_at }}
          </p>

          <h5 class="mt-4">Tasks</h5>
          <ul>
            <li v-for="task in milestoneDetails.tasks" :key="task.id">
              <input type="checkbox" :checked="task.is_completed" disabled />
              {{ task.description }}
            </li>
          </ul>
        </div>

        <div v-if="loading" class="d-flex justify-content-center my-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        <div v-if="error" class="alert alert-danger mt-4" role="alert">
          {{ error }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { fetchfunct } from '@/components/fetch.js'

const milestones = ref([])
const selectedMilestoneId = ref(null)
const milestoneDetails = ref(null)
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  loading.value = true

  const response = await fetchfunct('/student/milestone_management/individual')
  if (response.ok) {
    const data = await response.json()
    milestones.value = data.milestones
  } else {
    error.value = 'Failed to fetch milestones'
  }

  loading.value = false
})

const fetchMilestoneDetails = async () => {
  if (selectedMilestoneId.value !== null) {
    loading.value = true
    error.value = null

    const response = await fetchfunct(`/student/milestone_management/individual/${selectedMilestoneId.value}`)
    if (response.ok) {
      milestoneDetails.value = await response.json()
    } else {
      error.value = 'Error fetching milestone details'
    }

    loading.value = false
  }
}
</script>

<style scoped>
.individual-milestone-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.card {
  width: 100%;
  max-width: 600px;
}

.form-label {
  font-weight: bold;
}

.form-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg viewBox='0 0 16 16' fill='%23343a40' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='M7.255 8.387l4.52-4.52a.5.5 0 0 1 .708 0l.622.622a.5.5 0 0 1 0 .708L8.5 10.13a.5.5 0 0 1-.708 0L2.405 5.197a.5.5 0 0 1 0-.708l.622-.622a.5.5 0 0 1 .708 0l4.52 4.52z'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 16px 12px;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}
</style>
