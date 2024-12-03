<template>
  <nav class="navbar sticky-top navbar-expand-lg" data-bs-theme="dark">
    <div class="container-fluid">
      <RouterLink class="navbar-brand" to="/">
        <i class="bi bi-file-earmark-bar-graph"></i> Tracky
      </RouterLink>

      <button class="navbar-toggler" type="button" data-bs-toggle="offcanvas" data-bs-target="#Navbar">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="offcanvas offcanvas-end" tabindex="-1" id="Navbar">
        <div class="offcanvas-header">
          <h5 class="offcanvas-title" data-bs-dismiss="offcanvas">
            <RouterLink to="/" class="navbar-brand">
              <i class="bi bi-file-earmark-bar-graph"></i> Tracky
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

            <li class="nav-item" data-bs-dismiss="offcanvas">
              <RouterLink class="nav-link" to="/about">About</RouterLink>
            </li>
          </ul>

          <ul class="navbar-nav ms-auto">
            <li v-if="!identity.includes('Unauthenticated')" class="nav-item" data-bs-dismiss="offcanvas">
              <a class="nav-link pointer-link" @click="access_type_change('Logout')">
                <i class="bi bi-box-arrow-right"></i> Logout
              </a>
            </li>
            <li v-if="identity.includes('Unauthenticated') && !isHomePage" class="nav-item" data-bs-dismiss="offcanvas">
              <a class="nav-link pointer-link" @click="access_type_change('Login')">
                Login
              </a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </nav>
  <Access :access="access_type"></Access>
  <div v-for="(value, key) in useAlertStore().alerts" :key="key">
    <Alert :alert="value" :id="key"></Alert>
  </div>
  <RouterView />
</template>

<script setup>
  import { onMounted, watch, ref, computed } from 'vue'
  import { useRoute } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import { useIdentityStore } from './stores/identity.js'
  import { useAlertStore } from './stores/alert.js'
  import Access from '@/components/Access.vue'
  import Alert from '@/components/Alert.vue'

  const { identity } = storeToRefs( useIdentityStore() )
  const access_type = ref()
  const route = useRoute()

  // Computed property to check if the current route is home
  const isHomePage = computed( () => route.name === 'home' )

  onMounted( () =>
  {
    if ( localStorage.getItem( 'Authentication-Token' ) )
    {
      identity.value = JSON.parse( localStorage.getItem( 'Identity' ) ) || [
        'Unauthenticated',
      ]
    }
  } )

  watch( identity, () =>
  {
    const root = document.documentElement
    if ( identity.value.includes( 'Student' ) )
      root.style.setProperty( '--navbar-bg', '#2c3e50' )
    else if ( identity.value.includes( 'Instructor' ) )
      root.style.setProperty( '--navbar-bg', '#34495e' )
    else if ( identity.value.includes( 'TA' ) )
      root.style.setProperty( '--navbar-bg', '#1a2e5b' )
    else root.style.setProperty( '--navbar-bg', '#1e2a78' )
  } )

  function access_type_change ( value )
  {
    access_type.value = value
    new bootstrap.Modal( '#accessModal' ).show()
  }
</script>

<style scoped>

  /* Navbar styling */
  .navbar {
    background: linear-gradient(135deg, var(--navbar-bg), var(--gradient-end));
    box-shadow: var(--navbar-shadow);
    backdrop-filter: blur(10px);
    transition: all var(--transition-speed) ease;
    padding: 1rem 2rem;
  }

  /* Brand styling */
  .navbar-brand {
    font-size: 1.5rem;
    font-weight: 600;
    letter-spacing: 0.5px;
  }

  .navbar-brand i {
    position: relative;
    top: 0;
    transition: all 0.5s ease;
  }

  .navbar-brand:hover i {
    top: -5px;
    transform: scale(1.1);
  }

  /* Navigation links */
  .nav-link {
    font-weight: 500;
    padding: 0.5rem 1rem;
    margin: 0 0.25rem;
    border-radius: 4px;
    transition: all 0.3s ease;
    position: relative;
    color: rgba(255, 255, 255, 0.9) !important;
  }

  .nav-link:hover {
    color: white !important;
    background: rgba(255, 255, 255, 0.1);
    transform: translateY(-2px);
  }

  .nav-link::after {
    content: '';
    position: absolute;
    width: 0;
    height: 2px;
    bottom: 0;
    left: 50%;
    background-color: var(--accent-color);
    transition: all 0.3s ease;
  }

  .nav-link:hover::after {
    width: 100%;
    left: 0;
  }

  /* Active link styling */
  .router-link-active.nav-link {
    color: white !important;
    background: rgba(255, 255, 255, 0.15);
  }

  /* Button styling */
  .navbar-toggler {
    border: none;
    padding: 0.5rem;
    transition: transform 0.3s ease;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
  }

  .navbar-toggler:hover {
    transform: scale(1.05);
    background: rgba(255, 255, 255, 0.2);
  }

  @keyframes slideIn {
    from {
      transform: translateY(-20px);
      opacity: 0;
    }

    to {
      transform: translateY(0);
      opacity: 1;
    }
  }

  /* Router view transitions */
  .router-view-transition {
    transition: all 0.3s ease;
  }

  /* Pointer cursor for clickable items */
  .pointer-link {
    cursor: pointer;
  }

  /* Responsive adjustments */
  @media (max-width: 992px) {
    .navbar {
      padding: 0.75rem 1rem;
    }

    .nav-link {
      padding: 0.75rem 1rem;
      margin: 0.25rem 0;
      width: 100%;
      /* Make links full width */
    }

    .offcanvas {
      height: 100vh !important;
      background: linear-gradient(135deg, var(--navbar-bg), var(--gradient-end));
    }

    .offcanvas-body {
      flex-grow: 1;
      display: flex;
      flex-direction: column;
      padding: 1rem;
      /* Add some padding */
    }

    /* Make the nav items container full width */
    .offcanvas-body .navbar-nav {
      width: 100%;
    }

    /* Adjust spacing for nav items */
    .navbar-nav .nav-item {
      width: 100%;
      margin: 0.25rem 0;
    }

    /* Adjust the navbar brand in offcanvas header */
    .offcanvas-header .navbar-brand {
      margin-right: 0;
    }
  }
</style>
