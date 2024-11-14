<script setup>
    import { ref, computed, onMounted, onUnmounted } from 'vue'

    const props = defineProps( {
        options: {
            type: Array,
            required: true
        },
        modelValue: {
            type: [ String, Number ],
            default: null
        },
        placeholder: {
            type: String,
            default: 'Select a team'
        }
    } )

    const emit = defineEmits( [ 'update:modelValue', 'change' ] )

    const searchTerm = ref( '' )
    const isOpen = ref( false )
    const dropdownRef = ref( null )

    const filteredOptions = computed( () =>
    {
        if ( !searchTerm.value ) return props.options
        return props.options.filter( option =>
            option.name.toLowerCase().includes( searchTerm.value.toLowerCase() )
        )
    } )

    const selectedOption = computed( () =>
    {
        return props.options.find( option => option.id === props.modelValue )
    } )

    const handleSelect = ( option ) =>
    {
        emit( 'update:modelValue', option.id )
        emit( 'change', option.id )
        searchTerm.value = ''
        isOpen.value = false
    }

    // Close dropdown when clicking outside
    const handleClickOutside = ( event ) =>
    {
        if ( dropdownRef.value && !dropdownRef.value.contains( event.target ) )
        {
            isOpen.value = false
        }
    }

    // Add and remove click outside listener
    onMounted( () =>
    {
        document.addEventListener( 'click', handleClickOutside )
    } )

    onUnmounted( () =>
    {
        document.removeEventListener( 'click', handleClickOutside )
    } )
</script>

<template>
    <div class="searchable-dropdown" ref="dropdownRef">
        <div class="form-group">
            <div class="form-select d-flex justify-content-between align-items-center cursor-pointer"
                @click="isOpen = !isOpen">
                <span v-if="selectedOption">{{ selectedOption.name }}</span>
                <span v-else class="text-muted">{{ placeholder }}</span>
            </div>

            <div v-if="isOpen" class="dropdown-menu show w-100">
                <div class="px-3 py-2">
                    <input type="text" class="form-control" v-model="searchTerm" placeholder="Search teams..."
                        @click.stop>
                </div>
                <div class="dropdown-scrollable">
                    <template v-if="filteredOptions.length">
                        <button v-for="option in filteredOptions" :key="option.id" class="dropdown-item"
                            :class="{ 'active': option.id === modelValue }" @click="handleSelect(option)">
                            {{ option.name }}
                        </button>
                    </template>
                    <div v-else class="dropdown-item text-muted">
                        No results found
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
    .searchable-dropdown {
        position: relative;
    }

    .dropdown-menu {
        position: absolute;
        top: 100%;
        left: 0;
        z-index: 1000;
        margin-top: 0.125rem;
        border: 1px solid var(--navbar-bg);
        border-radius: 0.375rem;
        background-color: white;
        box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
    }

    .dropdown-scrollable {
        max-height: 200px;
        overflow-y: auto;
    }

    .dropdown-item {
        display: block;
        width: 100%;
        padding: 0.5rem 1rem;
        clear: both;
        text-align: inherit;
        white-space: nowrap;
        background-color: transparent;
        border: 0;
        cursor: pointer;
    }

    .dropdown-item:hover,
    .dropdown-item:focus {
        background: rgb(from var(--navbar-bg) r g b / 0.5);
    }

    .dropdown-item.active {
        background-color: var(--navbar-bg);
        color: white;
    }

    .cursor-pointer {
        cursor: pointer;
    }
</style>