<script setup>
    import { ref, onMounted } from 'vue'
    import { fetchfunct } from '@/components/fetch.js'
    import LoadingPlaceholder from '@/components/LoadingPlaceholder.vue'

    const milestones = ref( [] )
    const team_name = ref( "" )
    const loading = ref( true )
    const error = ref( null )

    onMounted( async () =>
    {
        loading.value = true
        const response = await fetchfunct( 'student/milestone_management/overall' )
        if ( response.ok )
        {
            const data = await response.json()
            milestones.value = data.milestones
            team_name.value = data.team_name
        } else
        {
            error.value = 'Failed to fetch milestones'
        }
        loading.value = false
    } )
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

            <div v-else>
                <div class="team-name-highlight mb-4">
                    <h5 class="text-uppercase mb-0">{{ team_name }}</h5>
                </div>

                <div class="card mb-4" v-for="milestone in milestones" :key="milestone.id">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center">
                            <div class="d-flex flex-column">
                                <h5 class="card-title mb-1">{{ milestone.title }}</h5>
                            </div>
                            <div class="text-end">
                                <h5 class="card-title mb-1">{{ milestone.completion_percentage }}%</h5>
                                <p class="card-subtitle mb-0 text-muted">Completed</p>
                            </div>
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

    .team-name-highlight {
        background-color: #f0f4f8;
        padding: 1rem;
        border-left: 4px solid var(--navbar-bg);
        border-radius: 4px;
        color: var(--navbar-bg);
    }

    .team-name-highlight h5 {
        font-weight: 600;
        letter-spacing: 0.5px;
        color: var(--navbar-bg);
        margin: 0;
    }
</style>
