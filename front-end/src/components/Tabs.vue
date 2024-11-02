<template>
    <div class="vh-100 d-flex">
        <div class="row flex-grow-1 g-0 w-100">
            <!-- Sidebar -->
            <aside class="col-md-3 col-lg-2 bg-light border-end d-flex flex-column h-100">
                <div class="flex-grow-1 d-flex">
                    <div class="d-flex flex-column align-items-center w-100 py-4 gap-2 mobile-nav-container">
                        <router-link v-for="tab in tabs" :key="tab.name" :to="tab.to"
                            class="btn w-75 text-start position-relative nav-link text-truncate" :class="{
                                'active text-white': $route.matched.filter(n=>n.name==tab.name).length,
                                'text-secondary': !$route.matched.filter(n=>n.name==tab.name).length
                            }" :title="tab.label">
                            <div class="d-flex align-items-center text-truncate">
                                <span class="text-truncate">{{ tab.label }}</span>
                            </div>
                        </router-link>
                    </div>
                </div>
            </aside>
            <!-- Main Content -->
            <main class="col-md-9 col-lg-10 p-4 h-100 overflow-auto">
                <router-view />
            </main>
        </div>
    </div>
</template>

<script setup>
    const props = defineProps( [ 'tabs' ] )
</script>

<style scoped>

    .nav-link {
        transition: all 0.3s ease;
        border-radius: 0.375rem;
        padding: 0.8rem 1rem;
        font-size: 0.9rem;
        max-width: 100%;
        overflow: hidden;
        white-space: nowrap;
    }

    .nav-link .d-flex {
        min-width: 0;
    }

    .nav-link.active {
        background-color: rgb(from var(--navbar-bg) r g b /0.8);
    }

    .nav-link:not(.active):hover {
        background-color: rgba(var(--bs-primary-rgb), 0.1);
        transform: translateX(2px);
    }

    /* Mobile Responsive Overrides */
    @media (max-width: 768px) {
        .vh-100 {
            height: auto !important;
        }

        aside {
            height: auto !important;
        }

        .mobile-nav-container {
            flex-direction: row !important;
            padding: 0.5rem !important;
            justify-content: center !important;
            flex-wrap: wrap;
        }

        .nav-link {
            width: auto !important;
            padding: 0.5rem 1rem;
            margin: 0.25rem;
        }
    }

    /* Extra small devices */
    @media (max-width: 576px) {
        .mobile-nav-container {
            gap: 0.5rem !important;
        }

        .nav-link {
            width: calc(50% - 1rem) !important;
            /* Account for margins */
            text-align: center !important;
        }
    }
</style>