<script setup>
import Tabs from '@/components/Tabs.vue'
</script>

<template>
  <Tabs
    :tabs="[
      {
        name: 'NotificationView',
        label: 'View Notifications',
        to: '/student/notification_management',
      },
      {
        name: 'NotificationPreference',
        label: 'Notification Preferences',
        to: '/student/notification_management/preference',
      },
    ]"
  >
  </Tabs>
</template>
