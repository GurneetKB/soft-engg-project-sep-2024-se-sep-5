<script setup>
  import { onMounted, watch, ref } from 'vue'
  import { RouterLink, RouterView } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import { useIdentityStore } from './stores/identity.js'
  import { useAlertStore } from './stores/alert.js'
  import Access from '@/components/Access.vue'
  import Alert from '@/components/Alert.vue'

  const { identity } = storeToRefs( useIdentityStore() )
  const access_type = ref()

  onMounted( () =>
  {
    if ( localStorage.getItem( "Authentication-Token" ) )
    {
      identity.value = JSON.parse( localStorage.getItem( "Identity" ) ) || [ 'Unauthenticated' ]
    }
  } )

  watch( identity, () =>
  {
    const root = document.documentElement
    if ( identity.value.includes( 'Student' ) )
      root.style.setProperty( '--navbar-bg', '#248afd' )
    else if ( identity.value.includes( 'Instructor' ) )
      root.style.setProperty( '--navbar-bg', '#1a55e3' )
    else if ( identity.value.includes( 'TA' ) )
      root.style.setProperty( '--navbar-bg', '#651FFF' )
    else
      root.style.setProperty( '--navbar-bg', '#5e6eed' )
  } )

  function access_type_change ( value )
  {
    access_type.value = value
    new bootstrap.Modal( '#accessModal' ).show()
  }

</script>

<template>

  <nav class="navbar sticky-top navbar-expand-lg">
    <div class="container-fluid">

      <RouterLink class="navbar-brand" to="/">
        Tracky
      </RouterLink>

      <button class="navbar-toggler" type="button" data-bs-toggle="offcanvas" data-bs-target="#Navbar">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="offcanvas offcanvas-end" tabindex="-1" id="Navbar">

        <div class="offcanvas-header">
          <h5 class="offcanvas-title" data-bs-dismiss="offcanvas">
            <RouterLink to="/" class="navbar-brand">
              Tracky
            </RouterLink>
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="offcanvas"></button>
        </div>

        <div class="offcanvas-body">
          <ul class="navbar-nav me-auto">

            <li v-if="identity.includes('Instructor') || identity.includes('TA')" class="nav-item"
              data-bs-dismiss="offcanvas">
              <RouterLink class="nav-link" to="/teacher/milestone_management">Milestone Management</RouterLink>
            </li>
            <li v-if="identity.includes('Instructor') || identity.includes('TA')" class="nav-item"
              data-bs-dismiss="offcanvas">
              <RouterLink class="nav-link" to="/teacher/team_management">Team Management</RouterLink>
            </li>

            <li v-if="identity.includes('Student')" class="nav-item" data-bs-dismiss="offcanvas">
              <RouterLink class="nav-link" to="/student/milestone_management">Milestone Management</RouterLink>
            </li>
            <li v-if="identity.includes('Student')" class="nav-item" data-bs-dismiss="offcanvas">
              <RouterLink class="nav-link" to="/student/notification_management">Notification Management</RouterLink>
            </li>

            <li v-if="!identity.includes('Unauthenticated')" class="nav-item" data-bs-dismiss="offcanvas">
              <a class="nav-link pointer-link" @click="access_type_change ( 'Logout' )">
                <i class="bi bi-box-arrow-right"></i>Logout
              </a>
            </li>
            <li v-if="identity.includes('Unauthenticated')" class="nav-item" data-bs-dismiss="offcanvas">
              <a class="nav-link pointer-link" @click="access_type_change ( 'Login' )">Login</a>
            </li>
          </ul>

          <ul class="navbar-nav ms-auto">
            <li class="nav-item" data-bs-dismiss="offcanvas">
              <RouterLink class="nav-link" to="/about">About</RouterLink>
            </li>
          </ul>

        </div>
      </div>
    </div>
  </nav>
  <Access :access="access_type"></Access>
  <div v-for="(value,key) in useAlertStore().alerts" :key="key">
    <Alert :alert="value" :id="key"></Alert>
  </div>
  <RouterView />
</template>

<style scoped>
  .navbar {
    background-color: var(--navbar-bg);
  }

  .router-link-exact-active.nav-link {
    color: var(--bs-navbar-active-color);
  }

  .router-link-exact-active.nav-link:hover {
    color: var(--bs-navbar-active-color);
  }

</style>