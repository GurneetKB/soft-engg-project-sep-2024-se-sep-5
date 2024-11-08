<script setup>
    import { ref, onMounted } from 'vue'
    import { fetchfunct } from '@/components/fetch.js'
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
            const response = await fetchfunct( `teacher/team_management/individual/github/${ selectedTeamId.value }` )
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
                <h4 class="m-0">Individual Team Github details</h4>
            </div>

            <LoadingPlaceholder v-if="loadingOnMount" variant="text" :count="3" :lines="[2]" spacing="p-4"
                :withBorder="true" />

            <div v-else class="form-group">
                <label for="team-select" class="form-label">Select a team</label>
                <select id="team-select" class="form-select" v-model="selectedTeamId" @change="fetchTeamDetails">
                    <option :value="null" disabled>Select a team</option>
                    <option v-for="team in teams" :key="team.id" :value="team.id">
                        {{ team.name }}
                    </option>
                </select>
            </div>

            <div v-if="teamDetails" class="mt-4">

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
<style scoped>
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
