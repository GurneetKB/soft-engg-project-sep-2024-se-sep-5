<script setup>
    import { onMounted } from 'vue';
    import { useAlertStore } from '@/stores/alert.js';

    const props = defineProps( { alert: Object, id: String } )

    onMounted( () => setTimeout( deletealert, 10000 ) )

    function deletealert ()
    {
        delete useAlertStore().alerts[ props.id ]
    }

    function icon ( type )
    {
        if ( type == 'alert-success' )
        {
            return '<i class="bi bi-check-circle-fill"></i>'
        }
        else if ( type == 'alert-info' )
        {
            return '<i class="bi bi-info-circle-fill"></i>'
        }
        else
        {
            return '<i class="bi bi-exclamation-triangle-fill"></i>'
        }
    }
</script>

<template>
    <div :id="props.id" :class="['alert',props.alert.type,'alert-dismissible','mx-auto']">
        <span v-html="icon(props.alert.type)"></span> {{ props.alert.msg }}
        <button class="btn-close" @click="deletealert" data-bs-dismiss="alert"></button>
        <div class="time-progress"></div>
    </div>
</template>

<style scoped>
    .alert {
        margin-top: 0.5%;
        width: 70%;
        animation: fadeOut 10s linear forwards;
    }

    .time-progress {
        width: 0;
        height: 4px;
        background: rgba(255, 255, 255, 0.3);
        position: absolute;
        bottom: 5px;
        left: 2%;
        border-radius: 3px;
        box-shadow:
            inset 0 1px 1px rgba(0, 0, 0, 0.05),
            0 -1px 0 rgba(255, 255, 255, 0.6);
        animation: runProgress 9s linear forwards 0.5s;
    }

    @keyframes fadeOut {
        0% {
            opacity: 0;
        }

        10% {
            opacity: 1;
        }

        90% {
            opacity: 1;
            transform: translateY(0px);
        }

        99% {
            opacity: 0;
            transform: translateY(-30px);
        }

        100% {
            opacity: 0;
        }
    }

    @keyframes runProgress {
        0% {
            width: 0%;
            background: rgba(255, 255, 255, 0.3);
        }

        100% {
            width: 96%;
            background: rgba(255, 255, 255, 1);
        }
    }

</style>