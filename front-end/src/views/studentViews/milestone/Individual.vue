<template>
  <div>
    <select v-model="selectedMilestoneId" @change="fetchMilestoneDetails">
      <option value="" disabled>Select a milestone</option>
      <option v-for="milestone in milestones" :key="milestone.id" :value="milestone.id">
        {{ milestone.title }}
      </option>
    </select>

    <div v-if="milestoneDetails">
      <h2>{{ milestoneDetails.title }}</h2>
      <p>{{ milestoneDetails.description }}</p>
      <p>Deadline: {{ milestoneDetails.deadline }}</p>
      <p>Created At: {{ milestoneDetails.created_at }}</p>
    </div>

    <LoadingPlaceholder v-if="loading" />
    <div v-if="error">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { fetchfunct } from '@/components/fetch.js'
import LoadingPlaceholder from '@/components/LoadingPlaceholder.vue'

const milestones = ref([])
const selectedMilestoneId = ref(null)
const milestoneDetails = ref(null)
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
    loading.value = true
    try {
        const response = await fetchfunct('/student/milestone_management/individual')
        if (response.ok) {
            const data = await response.json()
            milestones.value = data.milestones
        } else {
            error.value = 'Failed to fetch milestones'
        }
    } catch (err) {
        error.value = 'Error fetching milestones'
        console.error(err)
    } finally {
        loading.value = false
    }
})

const fetchMilestoneDetails = async () => {
    if (selectedMilestoneId.value) {
        loading.value = true
        try {
            const response = await fetch(`/student/milestone_management/individual/${selectedMilestoneId.value}`)
            if (response.ok) {
                milestoneDetails.value = await response.json()
            } else {
                console.error('Error fetching milestone details:', response.statusText)
            }
        } catch (err) {
            console.error('Error fetching milestone details:', err)
        } finally {
            loading.value = false
        }
    }
}
</script>
