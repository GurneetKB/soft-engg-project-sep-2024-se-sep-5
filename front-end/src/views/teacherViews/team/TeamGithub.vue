<script setup>
    import { ref, onMounted } from 'vue'
    import { fetchfunct } from '@/components/fetch.js'
    import SearchableDropdown from '@/components/SearchableDropdown.vue';
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

            </div>
        </div>
    </div>
</template>
<style scoped></style>
