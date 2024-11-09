<script setup>
    import Tabs from '@/components/Tabs.vue';
</script>

<template>
    <Tabs :tabs="[{ name: 'OverallView', label: 'Overall progress', to: '/student/milestone_management' },
        { name: 'IndividualView', label: 'Milestone-wise progress', to: '/student/milestone_management/individual' }]">
    </Tabs>
</template>