<script setup>
    import { ref, onMounted, computed } from 'vue'
    import { fetchfunct, checksuccess } from '@/components/fetch.js'
    import SearchableDropdown from '@/components/SearchableDropdown.vue';
    import LoadingPlaceholder from '@/components/LoadingPlaceholder.vue'
    import { convertUTCDateToLocaleDate, formatDate } from '@/components/date';

    const teams = ref( [] )
    const selectedTeamId = ref( null )
    const teamDetails = ref( null )
    const loadingOnMount = ref( true )
    const loading = ref( false )
    const error = ref( null )

    // Modal state
    const selectedTask = ref( null )
    const feedbackText = ref( '' )

    // Pagination
    const currentPage = ref( 1 )
    const milestonesPerPage = 1

    // Calculate total pages
    const totalPages = computed( () =>
    {
        if ( !teamDetails.value ) return 0
        return Math.ceil( teamDetails.value.length / milestonesPerPage )
    } )

    // Get paginated milestones
    const paginatedMilestones = computed( () =>
    {
        if ( !teamDetails.value ) return []
        const start = ( currentPage.value - 1 ) * milestonesPerPage
        const end = start + milestonesPerPage
        return teamDetails.value.slice( start, end )
    } )

    // Calculate completion rate for a milestone
    const calculateCompletionRate = ( milestone ) =>
    {
        if ( !milestone.tasks || milestone.tasks.length === 0 ) return 0
        const completedTasks = milestone.tasks.filter( task => task.is_completed ).length
        return Math.round( ( completedTasks / milestone.tasks.length ) * 100 )
    }

    // Check if task deadline has passed
    const isDeadlinePassed = ( is_completed, deadline ) =>
    {
        return convertUTCDateToLocaleDate( deadline ) < new Date() && !is_completed
    }

    // Get task status class and text
    const getTaskStatus = ( is_completed, deadline ) =>
    {
        if ( is_completed )
        {
            return {
                class: 'completed',
                badge: 'bg-success',
                text: 'Completed'
            }
        } else if ( isDeadlinePassed( is_completed, deadline ) )
        {
            return {
                class: 'overdue',
                badge: 'bg-danger',
                text: 'Overdue'
            }
        } else
        {
            return {
                class: 'pending',
                badge: 'bg-warning',
                text: 'Pending'
            }
        }
    }

    // Feedback methods
    const openFeedbackModal = ( task ) =>
    {
        selectedTask.value = task
        feedbackText.value = task.feedback || ''
        new bootstrap.Modal( '#feedbackModal' ).show()
    }

    const submitFeedback = async () =>
    {
        if ( !selectedTask.value ) return

        loading.value = true

        bootstrap.Modal.getInstance( "#feedbackModal" ).hide()

        const response = await fetchfunct( `teacher/team_management/individual/feedback/${ selectedTeamId.value }/${ selectedTask.value.task_id }`, {
            method: 'POST',
            body: JSON.stringify( { feedback: feedbackText.value } ),
            headers: { "Content-Type": "application/json" }
        } )

        if ( response.ok )
        {
            checksuccess( response )
            selectedTask.value.feedback = feedbackText.value
            selectedTask.value.feedback_time = new Date().toGMTString()
            error.value = null
        } else
        {
            error.value = 'Failed to submit feedback'
        }

        loading.value = false
    }

    const viewSubmission = async ( task ) =>
    {
        const response = await fetchfunct( `teacher/team_management/individual/submission/${ selectedTeamId.value }/${ task.task_id }` )
        if ( response.ok )
        {
            const blob = await response.blob()
            const url = window.URL.createObjectURL( blob )
            window.open( url, '_blank' )
            error.value = null
        } else
        {
            error.value = 'Failed to fetch submission'
        }
    }

    // Navigation methods
    const nextPage = () =>
    {
        if ( currentPage.value < totalPages.value )
        {
            currentPage.value++
        }
    }

    const prevPage = () =>
    {
        if ( currentPage.value > 1 )
        {
            currentPage.value--
        }
    }

    const goToPage = ( page ) =>
    {
        currentPage.value = page
    }

    onMounted( async () =>
    {
        loadingOnMount.value = true
        const response = await fetchfunct( 'teacher/team_management/individual' )
        if ( response.ok )
        {
            const data = await response.json()
            teams.value = data.teams
            error.value = null
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
            currentPage.value = 1
            const response = await fetchfunct( `teacher/team_management/individual/progress/${ selectedTeamId.value }` )
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
                <h4 class="m-0">Individual Team Progress</h4>
            </div>

            <LoadingPlaceholder v-if="loadingOnMount" variant="list-item" :count="5" />

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
                <div v-for="milestone in paginatedMilestones" :key="milestone.id" class="card mb-4">
                    <div class="card-body">
                        <div class="milestone-header d-flex justify-content-between align-items-center">
                            <h5 class="card-title">{{ milestone.title }}</h5>
                            <div class="completion-badge"
                                :class="calculateCompletionRate(milestone) === 100 ? 'bg-success' : 'bg-primary'">
                                {{ calculateCompletionRate(milestone) }}% Complete
                            </div>
                        </div>

                        <div class="progress mt-2 mb-3">
                            <div class="progress-bar" role="progressbar"
                                :style="{ width: calculateCompletionRate(milestone) + '%' }"
                                :aria-valuenow="calculateCompletionRate(milestone)" aria-valuemin="0"
                                aria-valuemax="100">
                            </div>
                        </div>

                        <p class="card-text">{{ milestone.description }}</p>

                        <div class="milestone-info mb-3">
                            <div class="row">
                                <div class="col-md-6">
                                    <p class="mb-2"><strong>Deadline:</strong> {{ formatDate(milestone.deadline) }}</p>
                                    <p class="mb-2"><strong>Created At:</strong> {{ formatDate(milestone.created_at) }}
                                    </p>
                                </div>
                                <div class="col-md-6">
                                    <p class="mb-2">
                                        <strong>Tasks Completed:</strong>
                                        {{ milestone.tasks.filter(task => task.is_completed).length }}/{{
                                        milestone.tasks.length }}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div class="tasks-container">
                            <h6 class="tasks-header mb-3">Tasks</h6>
                            <div class="task-list">
                                <div v-for="task in milestone.tasks" :key="task.task_id" class="task-item p-3 mb-2"
                                    :class="getTaskStatus(task.is_completed,milestone.deadline ).class">
                                    <div class="task-header d-flex justify-content-between align-items-center">
                                        <h6 class="mb-0">{{ task.description }}</h6>
                                        <div class="d-flex align-items-center gap-2">
                                            <span
                                                :class="`badge ${getTaskStatus(task.is_completed,milestone.deadline ).badge}`">
                                                {{getTaskStatus(task.is_completed,milestone.deadline).text }}
                                            </span>
                                            <!-- Add buttons for completed tasks -->
                                            <div v-if="task.is_completed" class="task-actions">
                                                <button class="btn btn-sm btn-primary me-2"
                                                    @click="viewSubmission(task)">
                                                    View PDF
                                                </button>
                                                <button class="btn btn-sm btn-secondary me-2"
                                                    @click="openFeedbackModal(task)">
                                                    {{ task.feedback ? 'Edit Feedback' : 'Give Feedback' }}
                                                </button>
                                                <button class="btn btn-sm nav-color-btn">
                                                    AI analysis
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                    <div v-if="task.feedback || task.feedback_time" class="task-feedback mt-2">
                                        <p v-if="task.feedback" class="mb-1">
                                            <strong>Feedback:</strong> {{ task.feedback }}
                                        </p>
                                        <p v-if="task.feedback_time" class="mb-0 text-muted">
                                            <small><strong>Feedback Time:</strong>
                                                {{ formatDate(task.feedback_time) }}</small>
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>


                <!-- Pagination -->
                <div v-if="totalPages > 1"
                    class="pagination-container d-flex justify-content-center align-items-center mt-4">
                    <button class="btn btn-outline-primary me-2" @click="prevPage" :disabled="currentPage === 1">
                        Previous
                    </button>
                    <div class="pagination-numbers mx-2">
                        <button v-for="page in totalPages" :key="page" class="btn btn-outline-primary mx-1"
                            :class="{ 'active': currentPage === page }" @click="goToPage(page)">
                            {{ page }}
                        </button>
                    </div>
                    <button class="btn btn-outline-primary ms-2" @click="nextPage"
                        :disabled="currentPage === totalPages">
                        Next
                    </button>
                </div>
            </div>
        </div>

        <!-- Feedback Modal -->
        <div class="modal" tabindex="-1" role="dialog" id="feedbackModal">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">{{ selectedTask?.feedback ? 'Edit Feedback' : 'Give Feedback' }}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <textarea class="form-control" v-model="feedbackText" rows="4"
                            placeholder="Enter your feedback here..."></textarea>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" @click="submitFeedback"
                            :disabled="loading">Submit</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
    .completion-badge {
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        color: white;
        font-weight: bold;
        font-size: 0.875rem;
    }

    .progress {
        height: 0.5rem;
        border-radius: 0.25rem;
        background-color: #e9ecef;
    }

    .progress-bar {
        background-color: #0d6efd;
        transition: width 0.6s ease;
    }

    .tasks-container {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
    }

    .tasks-header {
        color: #495057;
        font-weight: bold;
    }

    .task-item {
        background-color: white;
        border-radius: 0.375rem;
        border: 1px solid #dee2e6;
        transition: all 0.3s ease;
    }

    .task-item:hover {
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .task-item.completed {
        border-left: 4px solid #198754;
    }

    .task-item.pending {
        border-left: 4px solid #ffc107;
    }

    .task-feedback {
        background-color: #f8f9fa;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin-top: 0.5rem;
    }

    .pagination-container button.active {
        background-color: #0d6efd;
        color: white;
    }

    .milestone-info {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.375rem;
        margin: 1rem 0;
    }

    .task-actions {
        display: flex;
        gap: 0.5rem;
    }

    .btn-sm {
        padding: 0.25rem 0.5rem;
        font-size: 0.875rem;
    }

    .task-item.completed {
        border-left: 4px solid #198754;
    }

    .task-item.pending {
        border-left: 4px solid #ffc107;
    }

    .task-item.overdue {
        border-left: 4px solid #dc3545;
        background-color: #fff5f5;
    }

    .task-item.overdue .task-header h6 {
        color: #dc3545;
    }
</style>