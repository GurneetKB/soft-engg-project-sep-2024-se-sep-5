import { ref } from 'vue'
import { defineStore } from 'pinia'

// to push the alerts - the Alert component
export const useAlertStore = defineStore( 'alert', () =>
{

    const alerts = ref( {} )

    function alertpush ( list )
    {
        //push elements with unique key to alerts object
        list.map( e => { alerts.value[ window.crypto.randomUUID() ] = e } )

        // scroll to the top position of the screen to view the new alerts
        window.scrollTo( 0, 0 )
    }
    return { alerts, alertpush }
} )