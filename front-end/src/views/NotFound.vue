<script setup>
    import { useRouter } from 'vue-router'

    const router = useRouter()
</script>
<template>
    <a class="p-2 pointer-link icon-link icon-link-hover" @click="router.go(-1)">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-left"
            viewBox="0 0 16 16">
            <path fill-rule="evenodd"
                d="M15 8a.5.5 0 0 0-.5-.5H2.707l3.147-3.146a.5.5 0 1 0-.708-.708l-4 4a.5.5 0 0 0 0 .708l4 4a.5.5 0 0 0 .708-.708L2.707 8.5H14.5A.5.5 0 0 0 15 8" />
        </svg>
        Go back
    </a>
    <div class="text-center">
        <div><i class="bi bi-bug-fill" style="font-size:1000%"></i></div>
        <div>
            <h6 class="mb-3 p-2 text-muted">That's a 404</h6>
        </div>
        <div>
            <h5 class="p-2">The page you are looking for does not exist. Please recheck the typed URL.</h5>
        </div>
    </div>
</template>