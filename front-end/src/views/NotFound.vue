<script setup>
    import { useRouter } from 'vue-router'

    const router = useRouter()
</script>

<template>
    <div class="container-fluid vh-100 d-flex flex-column justify-content-center align-items-center bg-light">
        <div class="text-center p-5 bg-white shadow-lg rounded-4">
            <div class="mb-4">
                <i class="bi bi-compass nav-color" style="font-size: 8rem;"></i>
            </div>

            <div class="mb-4">
                <h1 class="display-4 nav-color fw-bold">404</h1>
                <h2 class="h4 text-muted mb-3">Page Not Found</h2>

                <p class="lead text-secondary mb-4">
                    Oops! It seems we've hit a detour. The page you're looking for
                    has wandered off the digital highway.
                </p>

                <div class="d-flex justify-content-center gap-3">
                    <button @click="router.back()" class="btn nav-color-btn-outline px-4 py-2 rounded-pill">
                        <i class="bi bi-arrow-left me-2"></i>Go Back
                    </button>

                    <router-link to="/" class="btn nav-color-btn px-4 py-2 rounded-pill">
                        <i class="bi bi-house me-2"></i>Home
                    </router-link>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
    .bg-light {
        background-color: #f8f9fa !important;
    }

    .bg-white {
        transition: transform 0.3s ease;
    }

    .bg-white:hover {
        transform: scale(1.02);
    }
</style>