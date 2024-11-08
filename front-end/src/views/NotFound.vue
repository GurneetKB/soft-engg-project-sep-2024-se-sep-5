<script setup>
    import { useRouter } from 'vue-router'

    const router = useRouter()
</script>
<template>
    <button @click="router.back()" class="p-2 btn btn-link text-decoration-none">
        ← Back
    </button>

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