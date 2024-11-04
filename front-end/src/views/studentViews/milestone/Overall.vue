<script setup>
    import { ref, onMounted } from 'vue'
    import { fetchfunct, checkerror } from '@/components/fetch.js'
    import LoadingPlaceholder from '@/components/LoadingPlaceholder.vue'

    const milestones = ref( [] )
    const loading = ref( true )
    const error = ref( null )

    onMounted( async () =>
    {
        loading.value = true
        const response = await fetchfunct( 'student/milestones' )
        if ( response.ok )
        {
            milestones.value = await response.json()
        } else
        {
            error.value = 'Failed to fetch milestones'
        }
        loading.value = false
    } )

    const calculateCompletionPercentage = ( milestone ) =>
    {
        const totalTasks = milestone.tasks.length
        const completedTasks = milestone.tasks.filter( task => task.completed ).length
        return ( completedTasks / totalTasks ) * 100
    }
</script>

<template>
    <div class="container-fluid p-4">
        <div class="milestone-progress-view max-w-800 mx-auto">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h4 class="m-0">Milestone Progress</h4>
            </div>

            <LoadingPlaceholder v-if="loading" variant="text" :count="3" :lines="[2]" spacing="p-4"
                :withBorder="true" />

            <div v-else-if="error" class="alert alert-danger">
                {{ error }}
            </div>

            <div v-else class="card mb-4" v-for="milestone in milestones" :key="milestone.id">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="d-flex flex-column">
                            <h5 class="card-title mb-1">{{ milestone.title }}</h5>
                            <p class="card-subtitle mb-0 text-muted">{{ milestone.team.name }}</p>
                        </div>
                        <div class="text-end">
                            <h5 class="card-title mb-1">{{ calculateCompletionPercentage(milestone).toFixed(0) }}%</h5>
                            <p class="card-subtitle mb-0 text-muted">Completed</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
    .max-w-800 {
        max-width: 800px;
    }

    .card {
        border-radius: 0.5rem;
        border: 1px solid #e9ecef;
    }

    .card-body {
        padding: 1.5rem;
    }
</style>