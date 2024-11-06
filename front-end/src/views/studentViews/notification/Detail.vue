<script setup>
    import { useRoute, useRouter } from 'vue-router'
    import { ref, onMounted } from 'vue'
    import { fetchfunct, checkerror } from '@/components/fetch.js'
    import LoadingPlaceholder from '@/components/LoadingPlaceholder.vue'
    import { convert_date_to_UTC } from '@/components/date.js'

    const route = useRoute()
    const router = useRouter()
    const notification = ref( null )
    const loading = ref( true )
    const error = ref( null )

    const formatDate = ( timestamp ) =>
    {
        return convert_date_to_UTC( timestamp ).toLocaleDateString( 'en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        } )
    }

    onMounted( async () =>
    {
        loading.value = true
        const id = route.params.id
        const response = await fetchfunct( 'student/notifications/' + id )
        if ( response.ok )
        {
            notification.value = await response.json()
            // Mark as read when viewing details
            if ( notification.value && !notification.value.read_at )
            {
                window.dispatchEvent( new CustomEvent( 'notification-read', {
                    detail: { id }
                } ) )
            }
        }
        else
        {
            checkerror( response )
            error.value = "Failed to fetch."
        }

        loading.value = false
    } )
</script>

<template>
    <div class="container-fluid p-4">
        <button @click="router.back()" class="btn btn-link text-decoration-none p-0">
            ← Back
        </button>

        <h4 class="mt-4 mb-4">Notification Detail</h4>


        <LoadingPlaceholder v-if="loading" variant="text" :count="1" :lines="[4, 2, 12, 12, 8]" spacing="p-4"
            :withBorder="false" />

        <div v-else-if="error" class="alert alert-danger">
            {{ error }}
        </div>

        <div v-else-if="notification" class="card">
            <div class="card-body">
                <h5 class="card-title mb-3">{{ notification.title }}</h5>
                <p class="text-muted small mb-4">
                    {{ formatDate(notification.read_at) }}
                </p>
                <div class="card-text" v-html="notification.message"></div>
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
        padding: 2rem;
    }
</style>