import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import Notfound from '@/views/NotFound.vue'
import { useAlertStore } from '@/stores/alert'
import { useIdentityStore } from '@/stores/identity'

const router = createRouter( {
  history: createWebHistory( import.meta.env.BASE_URL ),
  routes: [
    {
      path: '/',
      name: 'home',
      meta: {
        title: 'Tracky | The project tracker',
      },
      component: HomeView,
    },


    {
      path: '/about',
      name: 'about',
      meta: {
        title: 'About page',
      },
      component: () => import( '../views/AboutView.vue' ),
    },


    {
      path: '/student/milestone_management',
      name: 'StudentMilestoneView',
      meta: {
        title: 'Milestone management',
        auth_role: 'Student',
        requiresAuth: true
      },
      component: () =>
        import( '../views/studentViews/milestone/MilestoneTab.vue' ),
      children: [
        {
          path: '',
          name: 'OverallView',
          component: () =>
            import( '../views/studentViews/milestone/Overall.vue' ),
        },
        {
          path: 'individual',
          name: 'IndividualView',
          component: () =>
            import( '../views/studentViews/milestone/Individual.vue' ),
        },
      ],
    },


    {
      path: '/student/notification_management',
      meta: {
        title: 'Notification management',
        auth_role: 'Student',
        requiresAuth: true
      },
      component: () =>
        import( '../views/studentViews/notification/NotificationTab.vue' ),
      children: [
        {
          path: '',
          name: 'NotificationView',
          component: () =>
            import( '../views/studentViews/notification/List.vue' ),
          children: [
            {
              path: ':id',
              name: 'NotificationDetail',
              props: true,
              component: () =>
                import( '../views/studentViews/notification/Detail.vue' ),
            },
          ],
        },
        {
          path: 'preference',
          name: 'NotificationPreference',
          component: () =>
            import( '../views/studentViews/notification/Preference.vue' ),
        },
      ],
    },



    {
      path: '/teacher/milestone_management',
      name: 'MilestoneManagement',
      meta: {
        title: 'Milestone Management',
        auth_role: [ 'Instructor', 'TA' ],
        requiresAuth: true
      },
      component: () => import( '../views/teacherViews/milestone/MilestoneManagement.vue' ),
      children: [
        {
          path: 'add_milestone',
          name: 'AddMilestone',
          meta: {
            title: 'Add Milestone',
            auth_role: [ 'Instructor', 'TA' ],
            requiresAuth: true
          },
          component: () => import( '../views/teacherViews/milestone/AddMilestone.vue' ),
        },
        {
          path: 'edit_milestone/:id',
          name: 'EditMilestone',
          meta: {
            title: 'Edit Milestone',
            auth_role: [ 'Instructor', 'TA' ],
            requiresAuth: true
          },
          component: () => import( '../views/teacherViews/milestone/EditMilestone.vue' ),
          props: true
        },
      ]
    },


    {
      path: '/teacher/team_management',
      meta: {
        title: 'Team management',
        auth_role: [ 'Instructor', 'TA' ],
        requiresAuth: true
      },
      component: () =>
        import( '../views/teacherViews/team/TeamTab.vue' ),
      children: [
        {
          path: '',
          name: 'OverallTeamView',
          component: () =>
            import( '../views/teacherViews/team/TeamManagement.vue' )
        },
        {
          path: 'detail',
          name: 'TeamDetailView',
          component: () =>
            import( '../views/teacherViews/team/TeamDetail.vue' ),
        },
        {
          path: 'progress',
          name: 'TeamProgessView',
          component: () =>
            import( '../views/teacherViews/team/TeamProgress.vue' ),
        },
        {
          path: 'github_view',
          name: 'TeamGithubView',
          component: () =>
            import( '../views/teacherViews/team/TeamGithub.vue' ),
        },
      ],
    },

    {
      path: '/:pathMatch(.*)*',
      name: 'Notfound',
      component: Notfound,
    },
  ],


  scrollBehavior ( to, from, savedposition )
  {
    if ( savedposition ) return savedposition
    return { x: 0, y: 0 }
  },


} )

router.beforeEach( ( to, from ) =>
{
  document.title = to.meta.title || 'Tracky'

  if ( to.meta.requiresAuth )
  {
    let bool = true
    if ( typeof to.meta.auth_role === "string" )
    {
      bool = !useIdentityStore().identity.includes( to.meta.auth_role )
    }
    else if ( typeof to.meta.auth_role === "object" )
    {
      for ( const identity of to.meta.auth_role )
      {
        if ( useIdentityStore().identity.includes( identity ) )
        {
          bool = false
          break
        }
      }
    }
    if ( bool )
    {
      useAlertStore().alertpush( [
        {
          msg: "You don't have sufficient for this action! Please login with the correct account.",
          type: 'alert-danger',
        },
      ] )
      return {
        path: '/',
      }
    }
  }
} )

export default router
