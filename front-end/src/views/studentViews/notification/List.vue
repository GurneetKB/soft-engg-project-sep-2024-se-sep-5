<script setup>
    import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
    import { fetchfunct, checkerror, checksuccess } from '@/components/fetch.js'
    import LoadingPlaceholder from '@/components/LoadingPlaceholder.vue'

    const notifications = ref( [] )
    const loading = ref( true )

    const unreadCount = computed( () =>
    {
        return notifications.value.filter( n => !n.read_at ).length
    } )


    // Handler for notification read event
    const handleNotificationRead = ( event ) =>
    {
        const { id } = event.detail
        // Update the local notifications array
        notifications.value = notifications.value.map( notification =>
        {
            if ( notification.id == id )
            {
                return {
                    ...notification,
                    read_at: new Date().toUTCString()
                }
            }
            return notification
        } )
    }

    const markAllAsRead = async () =>
    {
        const response = await fetchfunct( 'student/notifications/mark_all_as_read' )
        if ( response.ok )
        {// Update all notifications locally
            notifications.value = notifications.value.map( notification => ( {
                ...notification,
                read_at: new Date().toUTCString()
            } ) )
            checksuccess( response )
        }
        else
        {
            checkerror( response )
        }
    }

    const formatDate = ( timestamp ) =>
    {
        return new Date( timestamp ).toLocaleDateString( 'en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        } )
    }

    onMounted( async () =>
    {
        loading.value = true
        const response = await fetchfunct( 'student/notifications' )
        if ( response.ok )
        {
            const data = await response.json()
            notifications.value = data.notifications
        }
        else
        {
            checkerror( response )
        }
        window.addEventListener( 'notification-read', handleNotificationRead )
        loading.value = false
    } )

    onBeforeUnmount( () =>
    {
        // Clean up event listener
        window.removeEventListener( 'notification-read', handleNotificationRead )
    } )
</script>

<template>
    <div class="container-fluid p-4">
        <!-- This div will be replaced by Detail.vue when a notification is clicked -->
        <router-view v-if="$route.params.id"></router-view>

        <!-- Show the list only when not viewing a detail -->
        <div v-else>
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h4 class="m-0">Notifications</h4>
                <div class="d-flex gap-3 align-items-center">
                    <span class="text-muted small">
                        {{ unreadCount }} unread
                    </span>
                    <button v-if="unreadCount > 0" @click="markAllAsRead" class="btn btn-sm nav-color-btn-outline">
                        Mark all as read
                    </button>
                </div>
            </div>

            <LoadingPlaceholder v-if="loading" variant="list-item" :count="5" :withLeadingIcon="true" :lines="[7, 4]"
                :leadingSize="8" />

            <div v-else-if="notifications.length === 0" class="text-center py-5 text-muted">
                <p>No notifications yet</p>
            </div>

            <div v-else>
                <router-link :to="{ 
            name: 'NotificationDetail', 
            params: { id: notification.id }
          }" v-for="notification in notifications" :key="notification.id" class="notification-item"
                    :class="{ 'unread': !notification.read_at }">
                    <div class="d-flex align-items-start gap-3 p-3">
                        <div v-if="!notification.read_at" class="notification-dot" aria-label="Unread notification">
                        </div>
                        <div class="flex-grow-1">
                            <h6 class="mb-1">{{ notification.title }}</h6>
                            <p class="text-muted small mb-0">
                                {{ formatDate(notification.created_at) }}
                            </p>
                        </div>
                    </div>
                </router-link>
            </div>
        </div>
    </div>
</template>
<style scoped>
    .notification-list {
        max-width: 800px;
        margin: 0 auto;
    }

    .notification-item {
        display: block;
        text-decoration: none;
        color: inherit;
        border-bottom: 1px solid #e9ecef;
        transition: background-color 0.2s ease;
    }

    .notification-item:hover {
        background-color: #f8f9fa;
    }

    .notification-item.unread {
        background-color: rgb(from var(--navbar-bg) r g b/0.05);
    }

    .notification-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: rgb(from var(--navbar-bg) r g b/0.8);
        margin-top: 8px;
    }

    /* Hover state */
    .notification-item:hover {
        background-color: rgba(var(--bs-primary-rgb), 0.1);
    }
</style>