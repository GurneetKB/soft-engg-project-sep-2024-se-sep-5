<script setup>
    import { ref, onMounted, computed } from 'vue'
    import { checkerror, fetchfunct } from './fetch';
    import sanitizeHtml from 'sanitize-html'
    import { marked } from 'marked'

    const messages = ref( [] )
    const newMessage = ref( '' )
    const isLoading = ref( false )
    const isChatOpen = ref( false )
    const isResizing = ref( false )
    const startX = ref( 0 )
    const startY = ref( 0 )
    const startWidth = ref( 300 )
    const startHeight = ref( 400 )
    const currentWidth = ref( 300 )
    const currentHeight = ref( 400 )

    const minWidth = 250
    const maxWidth = 500
    const minHeight = 300
    const maxHeight = window.innerHeight - 100

    const chatWindowStyle = computed( () => ( {
        width: `${ currentWidth.value }px`,
        height: `${ currentHeight.value }px`,
    } ) )

    const sendMessage = async () =>
    {
        if ( !newMessage.value.trim() || newMessage.value.length > 500 ) return

        const userMessage = newMessage.value
        messages.value.push( { text: userMessage, isUser: true } )
        newMessage.value = ''
        isLoading.value = true

        const response = await fetchfunct( 'student/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify( { message: userMessage } ),
        } )

        if ( response.ok )
        {
            const data = await response.json()
            messages.value.push( { text: sanitizeHtml( marked( data.analysis || '' ) ), isUser: false } )
        } else
        {
            checkerror( response )
        }
        isLoading.value = false
    }

    const toggleChat = () =>
    {
        isChatOpen.value = !isChatOpen.value
    }

    const startResize = ( event, direction ) =>
    {
        isResizing.value = true
        startX.value = event.clientX
        startY.value = event.clientY
        startWidth.value = currentWidth.value
        startHeight.value = currentHeight.value

        const resize = ( e ) =>
        {
            if ( !isResizing.value ) return

            if ( direction.includes( 'e' ) )
            {
                const newWidth = startWidth.value + ( e.clientX - startX.value )
                currentWidth.value = Math.max( minWidth, Math.min( newWidth, maxWidth ) )
            }
            if ( direction.includes( 's' ) )
            {
                const newHeight = startHeight.value + ( e.clientY - startY.value )
                currentHeight.value = Math.max( minHeight, Math.min( newHeight, maxHeight ) )
            }
            if ( direction.includes( 'w' ) )
            {
                const newWidth = startWidth.value - ( e.clientX - startX.value )
                currentWidth.value = Math.max( minWidth, Math.min( newWidth, maxWidth ) )
            }
            if ( direction.includes( 'n' ) )
            {
                const newHeight = startHeight.value - ( e.clientY - startY.value )
                currentHeight.value = Math.max( minHeight, Math.min( newHeight, maxHeight ) )
            }
        }

        const stopResize = () =>
        {
            isResizing.value = false
            document.removeEventListener( 'mousemove', resize )
            document.removeEventListener( 'mouseup', stopResize )
        }

        document.addEventListener( 'mousemove', resize )
        document.addEventListener( 'mouseup', stopResize )
    }

    onMounted( () =>
    {
        messages.value.push( { text: "Hello! I'm here to help you with your milestone projects. What questions do you have?", isUser: false } )
    } )
</script>

<template>
    <div class="chatbot-container" :class="{ 'open': isChatOpen }">
        <button @click="toggleChat" class="chat-toggle-btn">
            <i class="bi" :class="isChatOpen ? 'bi-x-lg' : 'bi-chat-dots-fill'"></i>
        </button>
        <div v-if="isChatOpen" class="chat-window" :style="chatWindowStyle">
            <div class="resize-handle n" @mousedown="(e) => startResize(e, 'n')"></div>
            <div class="resize-handle e" @mousedown="(e) => startResize(e, 'e')"></div>
            <div class="resize-handle s" @mousedown="(e) => startResize(e, 's')"></div>
            <div class="resize-handle w" @mousedown="(e) => startResize(e, 'w')"></div>
            <div class="resize-handle ne" @mousedown="(e) => startResize(e, 'ne')"></div>
            <div class="resize-handle se" @mousedown="(e) => startResize(e, 'se')"></div>
            <div class="resize-handle sw" @mousedown="(e) => startResize(e, 'sw')"></div>
            <div class="resize-handle nw" @mousedown="(e) => startResize(e, 'nw')"></div>
            <div class="messages-container">
                <div v-for="(message, index) in messages" :key="index"
                    :class="['message', { 'user-message': message.isUser, 'ai-message': !message.isUser }]"
                    v-html="message.text">
                </div>
                <div v-if="isLoading" class="message ai-message loading-message">
                    <div class="loading-indicator">
                        <div class="loading-dot"></div>
                        <div class="loading-dot"></div>
                        <div class="loading-dot"></div>
                    </div>
                    <div class="loading-text">AI is thinking...</div>
                </div>
            </div>
            <div class="input-container">
                <input v-model="newMessage" @keyup.enter="sendMessage" placeholder="Type your question here..."
                    :disabled="isLoading" maxlength="500" />
                <button @click="sendMessage" :disabled="isLoading">
                    <i class="bi" :class="isLoading ? 'bi-hourglass-split' : 'bi-send'"></i>
                </button>
            </div>
        </div>
    </div>
</template>

<style scoped>
    .chatbot-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 2000;
    }

    .chat-toggle-btn {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: var(--navbar-bg);
        color: white;
        border: none;
        font-size: 24px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .chat-toggle-btn:hover {
        transform: scale(1.1);
    }

    .chat-window {
        position: absolute;
        bottom: 70px;
        right: 0;
        background: white;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        resize: both;
        min-width: 250px;
        min-height: 300px;
        max-width: 500px;
        max-height: calc(100vh - 100px);
        border: 1px solid var(--navbar-bg);
    }

    .resize-handle {
        position: absolute;
        background-color: var(--navbar-bg);
        opacity: 0;
        transition: opacity 0.3s;
    }

    .resize-handle:hover {
        opacity: 0.3 !important;
    }

    .resize-handle.n,
    .resize-handle.s {
        left: 0;
        right: 0;
        height: 5px;
        cursor: ns-resize;
    }

    .resize-handle.e,
    .resize-handle.w {
        top: 0;
        bottom: 0;
        width: 5px;
        cursor: ew-resize;
    }

    .resize-handle.n {
        top: 0;
    }

    .resize-handle.s {
        bottom: 0;
    }

    .resize-handle.e {
        right: 0;
    }

    .resize-handle.w {
        left: 0;
    }

    .resize-handle.ne,
    .resize-handle.nw,
    .resize-handle.se,
    .resize-handle.sw {
        width: 10px;
        height: 10px;
    }

    .resize-handle.ne {
        top: 0;
        right: 0;
        cursor: ne-resize;
    }

    .resize-handle.nw {
        top: 0;
        left: 0;
        cursor: nw-resize;
    }

    .resize-handle.se {
        bottom: 0;
        right: 0;
        cursor: se-resize;
    }

    .resize-handle.sw {
        bottom: 0;
        left: 0;
        cursor: sw-resize;
    }

    .messages-container {
        flex-grow: 1;
        overflow-y: auto;
        padding: 10px;
        display: flex;
        flex-direction: column;
    }

    .message {
        margin-bottom: 10px;
        padding: 8px;
        border-radius: 8px;
        max-width: 80%;
    }

    .user-message {
        background-color: var(--navbar-bg);
        color: white;
        align-self: flex-end;
    }

    .ai-message {
        background-color: #f0f0f0;
        color: black;
        align-self: flex-start;
    }

    .input-container {
        display: flex;
        padding: 10px;
        background-color: #f0f0f0;
    }

    .input-container input {
        flex-grow: 1;
        padding: 8px;
        border: 1px solid #ccc;
        border-radius: 4px;
        margin-right: 5px;
    }

    .input-container button {
        padding: 8px 12px;
        background-color: var(--navbar-bg);
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

    .input-container button:disabled {
        background-color: #cccccc;
        cursor: not-allowed;
    }

    .loading-message {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 10px;
    }

    .loading-indicator {
        display: flex;
        justify-content: center;
        margin-bottom: 5px;
    }

    .loading-dot {
        width: 8px;
        height: 8px;
        background-color: var(--navbar-bg);
        border-radius: 50%;
        margin: 0 4px;
        animation: pulse 1.5s infinite ease-in-out;
    }

    .loading-dot:nth-child(2) {
        animation-delay: 0.5s;
    }

    .loading-dot:nth-child(3) {
        animation-delay: 1s;
    }

    .loading-text {
        font-size: 14px;
        color: #666;
    }

    @keyframes pulse {

        0%,
        100% {
            transform: scale(0.8);
            opacity: 0.5;
        }

        50% {
            transform: scale(1.2);
            opacity: 1;
        }
    }
</style>