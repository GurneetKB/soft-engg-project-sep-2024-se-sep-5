<script setup>
    import { ref, onMounted } from 'vue'
    import { fetchfunct, checkerror, checksuccess } from '@/components/fetch.js'
    import LoadingPlaceholder from '@/components/LoadingPlaceholder.vue'

    const preferences = ref( {
        email_deadline_notifications: false,
        in_app_deadline_notifications: false,
        email_feedback_notifications: false,
        in_app_feedback_notifications: false
    } )

    const loading = ref( true )
    const saving = ref( false )
    const error = ref( null )

    const preferenceDescriptions = {
        email_deadline_notifications: {
            title: 'Deadline Email Notifications',
            description: 'Receive email notifications about upcoming project deadlines and milestones'
        },
        in_app_deadline_notifications: {
            title: 'In-App Deadline Notifications',
            description: 'Get notifications within the app about upcoming deadlines and milestones'
        },
        email_feedback_notifications: {
            title: 'Feedback Email Notifications',
            description: 'Receive email notifications when instructors or TAs provide feedback'
        },
        in_app_feedback_notifications: {
            title: 'In-App Feedback Notifications',
            description: 'Get notifications within the app when new feedback is available'
        }
    }

    const loadPreferences = async () =>
    {

        loading.value = true
        const response = await fetchfunct( 'student/notifications/preferences' )
        if ( response.ok )
        {
            const data = await response.json()
            preferences.value = {
                ...preferences.value,
                ...data
            }
        } else
        {

            error.value = "Failed to load preferences"
        }

        loading.value = false

    }

    const savePreferences = async () =>
    {
        saving.value = true
        const response = await fetchfunct( 'student/notifications/preferences', {
            method: 'PUT',
            body: JSON.stringify( preferences.value ),
            headers: {
                "Content-Type": "application/json"
            }
        } )

        if ( response.ok )
        {
            checksuccess( response )
        } else
        {
            error.value = "Failed to save preferences"
        }

        saving.value = false

    }

    onMounted( () =>
    {
        loadPreferences()
    } )
</script>

<template>
    <div class="container-fluid p-4">
        <div class="notification-preferences max-w-800 mx-auto">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h4 class="m-0">Notification Preferences</h4>
            </div>

            <LoadingPlaceholder v-if="loading" variant="text" :count="4" :lines="[2]" spacing="p-4"
                :withBorder="true" />

            <div v-else-if="error" class="alert alert-danger">
                {{ error }}
            </div>

            <div v-else class="card">
                <div class="card-body">
                    <p class="text-muted mb-4">
                        Customize how you want to receive notifications about your projects and feedback.
                    </p>

                    <!-- Preferences Groups -->
                    <div class="preferences-group mb-4">
                        <h5 class="mb-3">Deadline Notifications</h5>
                        <div class="form-check form-switch mb-3">
                            <input class="form-check-input" type="checkbox" id="email_deadline_notifications"
                                v-model="preferences.email_deadline_notifications">
                            <label class="form-check-label" for="email_deadline_notifications">
                                <div class="d-flex flex-column">
                                    <span
                                        class="fw-medium">{{ preferenceDescriptions.email_deadline_notifications.title }}</span>
                                    <small
                                        class="text-muted">{{ preferenceDescriptions.email_deadline_notifications.description }}</small>
                                </div>
                            </label>
                        </div>
                        <div class="form-check form-switch mb-3">
                            <input class="form-check-input" type="checkbox" id="in_app_deadline_notifications"
                                v-model="preferences.in_app_deadline_notifications">
                            <label class="form-check-label" for="in_app_deadline_notifications">
                                <div class="d-flex flex-column">
                                    <span
                                        class="fw-medium">{{ preferenceDescriptions.in_app_deadline_notifications.title }}</span>
                                    <small
                                        class="text-muted">{{ preferenceDescriptions.in_app_deadline_notifications.description }}</small>
                                </div>
                            </label>
                        </div>
                    </div>

                    <div class="preferences-group mb-4">
                        <h5 class="mb-3">Feedback Notifications</h5>
                        <div class="form-check form-switch mb-3">
                            <input class="form-check-input" type="checkbox" id="email_feedback_notifications"
                                v-model="preferences.email_feedback_notifications">
                            <label class="form-check-label" for="email_feedback_notifications">
                                <div class="d-flex flex-column">
                                    <span
                                        class="fw-medium">{{ preferenceDescriptions.email_feedback_notifications.title }}</span>
                                    <small
                                        class="text-muted">{{ preferenceDescriptions.email_feedback_notifications.description }}</small>
                                </div>
                            </label>
                        </div>
                        <div class="form-check form-switch mb-3">
                            <input class="form-check-input" type="checkbox" id="in_app_feedback_notifications"
                                v-model="preferences.in_app_feedback_notifications">
                            <label class="form-check-label" for="in_app_feedback_notifications">
                                <div class="d-flex flex-column">
                                    <span
                                        class="fw-medium">{{ preferenceDescriptions.in_app_feedback_notifications.title }}</span>
                                    <small
                                        class="text-muted">{{ preferenceDescriptions.in_app_feedback_notifications.description }}</small>
                                </div>
                            </label>
                        </div>
                    </div>

                    <div class="d-flex justify-content-end">
                        <button class="btn btn-primary" @click="savePreferences" :disabled="saving">
                            <span v-if="saving" class="spinner-border spinner-border-sm me-2" role="status"></span>
                            {{ saving ? 'Saving...' : 'Save Preferences' }}
                        </button>
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

    .preferences-group {
        border-bottom: 1px solid #e9ecef;
    }

    .preferences-group:last-child {
        border-bottom: none;
    }

    .form-check-input {
        cursor: pointer;
    }

    .form-check-label {
        cursor: pointer;
        padding-left: 0.5rem;
    }
</style>