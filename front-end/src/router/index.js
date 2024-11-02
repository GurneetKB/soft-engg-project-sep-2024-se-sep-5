import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import Notfound from '@/views/NotFound.vue'
import { useAlertStore } from '@/stores/alert'

const router = createRouter( {
  history: createWebHistory( import.meta.env.BASE_URL ),
  routes: [
    {
      path: '/',
      name: 'home',
      meta: {
        title: 'Tracky | The project tracker',
      },
      component: HomeView
    },
    {
      path: '/about',
      name: 'about',
      meta: {
        title: 'About page',
      },
      component: () => import( '../views/AboutView.vue' )
    },
    {
      path: '/student/milestone_management',
      name: 'StudentMilestoneView',
      meta: {
        title: 'Milestone management',
        auth_role: 'Student'
      },
      component: () => import( '../views/studentViews/milestone/MilestoneTab.vue' )
    },
    {
      path: '/student/notification_management',
      name: 'Notification',
      meta: {
        title: 'Notification management',
        auth_role: 'Student'
      },
      component: () => import( '../views/studentViews/notification/NotificationTab.vue' ),
      children: [
        {
          path: '',
          name: 'NotificationView',
          component: () => import( '../views/studentViews/notification/List.vue' )
        },
        {
          path: 'preference',
          name: 'NotificationPreference',
          component: () => import( '../views/studentViews/notification/Preference.vue' )
        }

      ],
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'Notfound',
      component: Notfound
    },
  ],
  scrollBehavior ( to, from, savedposition )
  {
    if ( savedposition ) return savedposition
    return { x: 0, y: 0 }
  }
} )

router.beforeEach( ( to, from ) =>
{
  document.title = to.meta.title || 'Tracky'

  if ( to.meta.requiresAuth )
  {
    if ( !useIdentityStore().identity.includes( to.meta.auth_role ) )
    {
      useAlertStore().alertpush( [ { msg: "You don't have sufficient for this action! Please login with the correct account.", type: 'alert-danger' } ] )
      return {
        path: '/'
      }
    }
  }
}
)

export default router
