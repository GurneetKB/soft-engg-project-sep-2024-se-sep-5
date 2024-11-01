import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useIdentityStore = defineStore( 'identity', () =>
{
  const identity = ref( "Unauthenticated" )
  return { identity }
} )
