<script setup>
    const props = defineProps( {
        // Core props
        variant: {
            type: String,
            default: 'text',
            validator: ( value ) => [
                'list-item',
                'card',
                'text',
                'table',
                'form',
                'custom'
            ].includes( value )
        },
        count: {
            type: Number,
            default: 1
        },
        lines: {
            type: Array,
            default: () => [ 6 ]
        },

        // Styling props
        spacing: {
            type: String,
            default: 'p-3'
        },
        withBorder: {
            type: Boolean,
            default: true
        },
        animation: {
            type: String,
            default: 'glow',
            validator: ( value ) => [ 'glow', 'wave' ].includes( value )
        },

        // List item specific props
        withLeadingIcon: {
            type: Boolean,
            default: false
        },
        leadingSize: {
            type: Number,
            default: 24
        },

        // Card specific props
        withImage: {
            type: Boolean,
            default: false
        },
        imageHeight: {
            type: Number,
            default: 200
        },
        fullHeight: {
            type: Boolean,
            default: false
        },
        // Form specific props
        formFields: {
            type: Array,
            default: () => [
                { type: 'text' },
                { type: 'text' },
                { type: 'textarea' }
            ]
        }
    } )
</script>
<template>
    <div class="placeholder-glow" :class="{ 'border-bottom': withBorder }">
        <div v-for="i in count" :key="i" class="placeholder-item" :class="[spacing]">
            <template v-if="variant === 'form'">
                <div v-for="(field, index) in formFields" :key="index" class="mb-4">
                    <!-- Label placeholder -->
                    <span class="placeholder d-block mb-2" style="height: 1.2rem; width: 120px;"></span>

                    <!-- Input field placeholder -->
                    <span class="placeholder d-block" :style="{ 
                            height: field.type === 'textarea' ? '100px' : '38px',
                            width: '100%'
                        }" :class="field.type === 'textarea' ? 'rounded' : 'rounded-2'"></span>
                </div>

                <!-- Button placeholder -->
                <div class="d-flex justify-content-center mt-4">
                    <span class="placeholder rounded-2" style="height: 40px; width: 150px;"></span>
                </div>
            </template>

            <template v-if="variant === 'list-item'">
                <!-- List item with optional avatar/icon -->
                <div class="d-flex align-items-start gap-3">
                    <span v-if="withLeadingIcon" class="placeholder rounded-circle" :style="{
                            width: `${leadingSize}px`,
                            height: `${leadingSize}px`
                        }"></span>
                    <div class="flex-grow-1">
                        <span class="placeholder mb-2" :class="[`col-${lines[0] || 7}`]"></span>
                        <template v-for="(width, index) in lines.slice(1)" :key="index">
                            <span class="placeholder d-block" :class="[`col-${width}`]" :style="{ 
                                    marginBottom: index < lines.length - 2 ? '0.5rem' : '0'
                                }"></span>
                        </template>
                    </div>
                </div>
            </template>

            <template v-else-if="variant === 'card'">
                <!-- Card-style placeholder -->
                <div class="card" :class="{ 'h-100': fullHeight }">
                    <span v-if="withImage" class="placeholder w-100" :style="{ height: `${imageHeight}px` }"></span>
                    <div class="card-body">
                        <template v-for="(width, index) in lines" :key="index">
                            <span class="placeholder d-block" :class="[`col-${width}`]" :style="{ 
                                    marginBottom: index < lines.length - 1 ? '0.5rem' : '0'
                                }"></span>
                        </template>
                    </div>
                </div>
            </template>

            <template v-else-if="variant === 'text'">
                <!-- Text-only placeholder -->
                <template v-for="(width, index) in lines" :key="index">
                    <span class="placeholder d-block" :class="[`col-${width}`]" :style="{ 
                            marginBottom: index < lines.length - 1 ? '0.5rem' : '0'
                        }"></span>
                </template>
            </template>

            <template v-else-if="variant === 'table'">
                <!-- Table row placeholder -->
                <div class="d-flex gap-3">
                    <span v-for="(width, index) in lines" :key="index" class="placeholder"
                        :class="[`col-${width}`]"></span>
                </div>
            </template>

            <template v-else-if="variant === 'custom'">
                <slot></slot>
            </template>
        </div>
    </div>
</template>

<style scoped>
    .placeholder-item:last-child {
        border-bottom: none;
    }

    .placeholder {
        height: 1rem;
    }

    /* Add subtle variation to placeholder colors for more realistic look */
    .placeholder:nth-child(3n) {
        opacity: 0.9;
    }

    .placeholder:nth-child(3n+1) {
        opacity: 0.8;
    }

    /* Rounded corners for form fields */
    .placeholder.rounded-2 {
        border-radius: 0.375rem !important;
    }
</style>