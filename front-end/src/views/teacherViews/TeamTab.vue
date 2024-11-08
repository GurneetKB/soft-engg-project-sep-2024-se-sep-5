<script setup>
    import Tabs from '@/components/Tabs.vue';
</script>

<template>
    <Tabs :tabs="[{ name: 'OverallTeamView', label: 'Overall team progress', to: '/teacher/team_management' },
  { name: 'TeamDetailView', label: 'Individual team detail', to: '/teacher/team_management/detail' },
  {name: 'TeamProgessView', label: 'Individual team progress', to: '/teacher/team_management/progress'},
  {name: 'TeamGithubView', label: 'Individual github view', to: '/teacher/team_management/github_view'}]">
    </Tabs>
</template>