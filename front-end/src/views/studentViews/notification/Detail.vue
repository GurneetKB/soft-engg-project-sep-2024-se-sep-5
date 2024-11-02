<script setup>
    import { ref, onMounted } from 'vue'
    import { useRoute, useRouter } from 'vue-router'

    const route = useRoute()
    const router = useRouter()
    const notification = ref( null )
    const loading = ref( true )
    const error = ref( null )

    const fetchNotificationDetail = async () =>
    {
        try
        {
            loading.value = true
            // Replace with your actual API call
            const response = await fetch( `/api/notifications/${ route.params.id }` )
            if ( !response.ok ) throw new Error( 'Notification not found' )
            const data = await response.json()
            notification.value = data

            // Mark as read if it wasn't already
            if ( !data.read )
            {
                await fetch( `/api/notifications/${ route.params.id }/mark-read`, {
                    method: 'POST'
                } )
            }
        } catch ( err )
        {
            error.value = 'Failed to load notification'
            console.error( 'Error fetching notification:', err )
        } finally
        {
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

    onMounted( () =>
    {
        fetchNotificationDetail()
    } )
</script>

<template>
    <div class="container-fluid p-4">
        <div class="notification-detail max-w-800 mx-auto">
            <div class="d-flex align-items-center gap-3 mb-4">
                <button @click="router.back()" class="btn btn-link text-decoration-none p-0">
                    ← Back
                </button>
                <h4 class="m-0">Notification Detail</h4>
            </div>

            <LoadingPlaceholder v-if="loading" variant="text" :count="1" :lines="[4, 2, 12, 12, 8]" spacing="p-4"
                :withBorder="false" />

            <div v-else-if="error" class="alert alert-danger">
                {{ error }}
            </div>

            <div v-else-if="notification" class="card">
                <div class="card-body">
                    <h5 class="card-title mb-3">{{ notification.title }}</h5>
                    <p class="text-muted small mb-4">
                        {{ formatDate(notification.timestamp) }}
                    </p>
                    <div class="card-text" v-html="notification.content"></div>
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
        padding: 2rem;
    }
</style>