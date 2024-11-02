import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { configure } from 'vee-validate'
import App from './App.vue'
import router from './router'


configure( {
    validateOnInput: true,
} )

const app = createApp( App )

app.use( createPinia() )
app.use( router )

app.mount( '#app' )