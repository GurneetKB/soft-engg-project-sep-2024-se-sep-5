<template>

    <div class="container-fluid p-4">
        <div class="milestone-progress-view max-w-800 mx-auto">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h4 class="m-0">Individual Milestone</h4>
            </div>

            <LoadingPlaceholder v-if="loadingOnMount" variant="text" :count="3" :lines="[2]" spacing="p-4"
                :withBorder="true" />

            <div v-else class="form-group">
                <label for="milestone-select" class="form-label">Select a Milestone</label>
                <select id="milestone-select" class="form-select" v-model="selectedMilestoneId"
                    @change="fetchMilestoneDetails">
                    <option :value="null" disabled>Milestones</option>
                    <option v-for="milestone in milestones" :key="milestone.id" :value="milestone.id">
                        {{ milestone.title }}
                    </option>
                </select>
            </div>

            <div v-if="milestoneDetails" class="mt-4">
                <div class="milestone-card card mb-4">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center">
                            <div class="d-flex flex-column">
                                <div class="milestone-name-highlight mb-4">
                                    <h5 class="card-title">{{ milestoneDetails.title }}</h5>
                                </div>
                                <p class="card-subtitle mb-0 text-muted">{{ milestoneDetails.description }}</p>
                            </div>
                        </div>
                        <div class="mt-3">
                            <p class="mb-2">
                                <strong>Deadline:</strong> {{ formatDate(milestoneDetails.deadline) }}
                            </p>
                            <p class="mb-0">
                                <strong>Created At:</strong> {{ formatDate(milestoneDetails.created_at) }}
                            </p>
                        </div>
                    </div>
                </div>

                <div>
                    <h5 class="mb-3">Tasks</h5>
                    <ul class="list-group">
                        <li class="list-group-item" v-for="task in milestoneDetails.tasks" :key="task.id">
                            <input type="checkbox" class="form-check-input" :checked="task.is_completed" disabled />
                            {{ task.description }}
                        </li>
                    </ul>
                </div>
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
</template>

<script setup>
    import { ref, onMounted } from 'vue'
    import { fetchfunct } from '@/components/fetch.js'
    import LoadingPlaceholder from '@/components/LoadingPlaceholder.vue'

    const milestones = ref( [] )
    const selectedMilestoneId = ref( null )
    const milestoneDetails = ref( null )
    const loadingOnMount = ref( true )
    const loading = ref( false )
    const error = ref( null )

    onMounted( async () =>
    {
        loadingOnMount.value = true

        const response = await fetchfunct( '/student/milestone_management/individual' )
        if ( response.ok )
        {
            const data = await response.json()
            milestones.value = data.milestones
        } else
        {
            error.value = 'Failed to fetch milestones'
        }

        loadingOnMount.value = false
    } )

    const fetchMilestoneDetails = async () =>
    {
        if ( selectedMilestoneId.value !== null )
        {
            loading.value = true
            error.value = null

            const response = await fetchfunct( `/student/milestone_management/individual/${ selectedMilestoneId.value }` )
            if ( response.ok )
            {
                milestoneDetails.value = await response.json()
                error.value = null
            } else
            {
                error.value = 'Error fetching milestone details'
            }

            loading.value = false
        }
    }

    const formatDate = ( timestamp ) =>
    {
        return new Date( timestamp ).toLocaleDateString( 'en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        } )
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
        border-radius: 0.5rem;
        border: 1px solid #e9ecef;
    }

    .card-header {
        background-color: #f0f4f8;
        border-top-left-radius: 0.5rem;
        border-top-right-radius: 0.5rem;
        padding: 1.5rem;
    }

    .card-body {
        padding: 1.5rem;
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

    .milestone-card {
        border-radius: 0.5rem;
        border: 1px solid #e9ecef;
    }

    .form-check-input:checked {
        background-color: green;
    }

    .milestone-name-highlight {
        background-color: #f0f4f8;
        padding: 1rem;
        border-left: 4px solid var(--navbar-bg);
        border-radius: 4px;
        color: var(--navbar-bg);
    }

    .milestone-name-highlight h5 {
        font-weight: 600;
        letter-spacing: 0.5px;
        color: var(--navbar-bg);
        margin: 0;
    }
</style>